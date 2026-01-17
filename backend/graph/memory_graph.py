"""
LangGraph agent pipeline for memory query processing with safety checks.
"""

from typing import TypedDict, List, Dict, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from retrieval.hybrid_retriever import get_retriever
from llm.router import generate_with_fallback, get_llm_provider
from config.settings import get_settings
import logging
import tiktoken  # For token counting

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """State passed between graph nodes."""
    user_id: str
    query: str
    intent: Optional[str]
    retrieved_entries: List[Dict]
    temporal_patterns: Optional[Dict]
    answer: Optional[str]
    evidence: List[Dict]
    llm_provider: Optional[str]
    safety_check_passed: bool


class MemoryGraph:
    """LangGraph workflow for processing memory queries with safety checks."""
    
    def __init__(self):
        self.settings = get_settings()
        self.retriever = get_retriever()
        self.graph = self._build_graph()
        
        # Initialize token counter (approximate)
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.tokenizer = None
            logger.warning("Could not initialize tokenizer, token counting will be approximate")
    
    async def _invoke_llm(self, messages):
        """
        Invoke LLM via router (provider-agnostic).
        Router handles all fallback logic internally.
        Never raises exceptions - returns response or safe fallback string.
        """
        return await generate_with_fallback(messages)
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text (approximate if tokenizer unavailable)."""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(text) // 4
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("intent_classifier", self.intent_classifier)
        workflow.add_node("memory_retriever", self.memory_retriever)
        workflow.add_node("evidence_safety_check", self.evidence_safety_check)
        workflow.add_node("temporal_analyzer", self.temporal_pattern_analyzer)
        workflow.add_node("reflection_synthesizer", self.reflection_synthesizer)
        
        # Define edges with conditional routing
        workflow.set_entry_point("intent_classifier")
        workflow.add_edge("intent_classifier", "memory_retriever")
        workflow.add_edge("memory_retriever", "evidence_safety_check")
        
        # Conditional: if safety check fails, skip to synthesizer with insufficient data message
        workflow.add_conditional_edges(
            "evidence_safety_check",
            self._route_after_safety_check,
            {
                "continue": "temporal_analyzer",
                "insufficient": "reflection_synthesizer"
            }
        )
        
        workflow.add_edge("temporal_analyzer", "reflection_synthesizer")
        workflow.add_edge("reflection_synthesizer", END)
        
        return workflow.compile()
    
    def _route_after_safety_check(self, state: GraphState) -> str:
        """Route based on safety check result."""
        return "continue" if state.get("safety_check_passed", False) else "insufficient"
    
    async def intent_classifier(self, state: GraphState) -> GraphState:
        """
        Classify user intent from query.
        """
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an intent classifier for a personal memory system.
            Classify the user's query into one of these categories:
            - reflection: Questions about feelings, emotions, or internal states (e.g., "Why do I feel burned out?")
            - pattern: Questions about patterns or trends (e.g., "When am I most productive?")
            - recall: Questions about specific events or memories (e.g., "What happened before my exam?")
            - temporal_comparison: Questions comparing different time periods (e.g., "How was January different from December?")
            - advice: Questions seeking guidance (e.g., "What should I do about my stress?")
            
            Respond with ONLY the intent category name, nothing else."""),
            HumanMessage(content=state["query"])
        ])
        
        response_text = await self._invoke_llm(prompt.format_messages())
        
        # Router always returns a string (never None)
        # Check if it's a fallback message
        if "I'm having trouble" in response_text:
            logger.warning("LLM returned fallback message for intent classification, using default 'recall'")
            intent = "recall"  # Safe default
        else:
            intent = response_text.strip().lower()
            
            # Validate intent
            valid_intents = ["reflection", "pattern", "recall", "temporal_comparison", "advice"]
            if intent not in valid_intents:
                intent = "recall"  # Default fallback
        
        logger.info(f"Intent classified: {intent} for query: {state['query'][:50]}...")
        
        llm_provider = get_llm_provider()
        return {**state, "intent": intent, "llm_provider": llm_provider}
    
    async def memory_retriever(self, state: GraphState) -> GraphState:
        """
        Retrieve relevant journal entries using hybrid retrieval.
        """
        query = state["query"]
        user_id = state["user_id"]
        
        # Extract temporal and mood filters from query
        time_filter = await self.retriever.extract_temporal_filters(query)
        mood_filter = await self.retriever.extract_mood_filter(query)
        
        # Retrieve entries (limited by settings)
        entries = await self.retriever.retrieve(
            user_id=user_id,
            query=query,
            limit=self.settings.MAX_RETRIEVED_MEMORIES,
            time_filter=time_filter,
            mood_filter=mood_filter,
            recency_weight=0.3,
            mood_weight=0.2
        )
        
        logger.info(f"Retrieved {len(entries)} entries for user {user_id[:8]}...")
        
        return {**state, "retrieved_entries": entries}
    
    async def evidence_safety_check(self, state: GraphState) -> GraphState:
        """
        Safety check: validate evidence before synthesis.
        Enforces minimum evidence threshold and relevance scores.
        """
        entries = state["retrieved_entries"]
        
        # Check minimum evidence threshold
        if len(entries) < self.settings.MIN_EVIDENCE_THRESHOLD:
            logger.warning(
                f"Insufficient evidence: {len(entries)} entries < threshold {self.settings.MIN_EVIDENCE_THRESHOLD}"
            )
            return {**state, "safety_check_passed": False}
        
        # Check relevance scores (if available)
        if entries:
            avg_score = sum(e.get("score", 0) for e in entries) / len(entries)
            if avg_score < self.settings.MIN_RELEVANCE_SCORE:
                logger.warning(
                    f"Low relevance: avg score {avg_score:.2f} < threshold {self.settings.MIN_RELEVANCE_SCORE}"
                )
                # Still allow but mark as low confidence
                return {**state, "safety_check_passed": True, "low_confidence": True}
        
        return {**state, "safety_check_passed": True, "low_confidence": False}
    
    async def temporal_pattern_analyzer(self, state: GraphState) -> GraphState:
        """
        Analyze temporal patterns in retrieved entries.
        """
        entries = state["retrieved_entries"]
        intent = state["intent"]
        
        if not entries:
            return {**state, "temporal_patterns": {}}
        
        # Only analyze patterns for relevant intents
        if intent not in ["pattern", "temporal_comparison", "reflection"]:
            return {**state, "temporal_patterns": {}}
        
        # Extract temporal information
        from datetime import datetime
        from collections import defaultdict
        
        patterns = {
            "time_of_day": defaultdict(int),
            "day_of_week": defaultdict(int),
            "month": defaultdict(int),
            "mood_distribution": defaultdict(int),
            "entry_count": len(entries)
        }
        
        for entry in entries:
            try:
                created_at = datetime.fromisoformat(entry["created_at"].replace('Z', '+00:00'))
                patterns["time_of_day"][created_at.hour] += 1
                patterns["day_of_week"][created_at.strftime("%A")] += 1
                patterns["month"][created_at.strftime("%B")] += 1
                
                if entry.get("mood"):
                    patterns["mood_distribution"][entry["mood"]] += 1
            except Exception:
                continue
        
        # Convert defaultdicts to regular dicts
        patterns = {
            k: dict(v) if isinstance(v, defaultdict) else v
            for k, v in patterns.items()
        }
        
        return {**state, "temporal_patterns": patterns}
    
    async def reflection_synthesizer(self, state: GraphState) -> GraphState:
        """
        Synthesize final answer from retrieved evidence with safety checks.
        """
        query = state["query"]
        intent = state["intent"]
        entries = state["retrieved_entries"]
        patterns = state.get("temporal_patterns", {})
        safety_passed = state.get("safety_check_passed", False)
        low_confidence = state.get("low_confidence", False)
        
        # Handle insufficient evidence
        if not safety_passed or not entries:
            answer = (
                "I don't have enough journal evidence to answer that question yet. "
                "Please write more entries first, especially entries related to this topic."
            )
            return {**state, "answer": answer, "evidence": []}
        
        # Build context from retrieved entries with token budget
        context_parts = []
        evidence = []
        total_tokens = self._count_tokens(query)
        max_context_tokens = self.settings.MAX_CONTEXT_TOKENS
        
        for i, entry in enumerate(entries):
            # Use entry_date if available, otherwise fallback to created_at
            date_str = entry.get("entry_date") or entry.get("created_at", "")
            if isinstance(date_str, str) and len(date_str) >= 10:
                date_str = date_str[:10]
            mood_str = f" (mood: {entry['mood']})" if entry.get("mood") else ""
            
            # Truncate content to fit token budget
            content = entry['content']
            entry_text = f"Entry {i+1} ({date_str}{mood_str}): {content}"
            entry_tokens = self._count_tokens(entry_text)
            
            # Check if adding this entry would exceed budget
            if total_tokens + entry_tokens > max_context_tokens:
                logger.warning(f"Token budget reached, using {i} entries out of {len(entries)}")
                break
            
            context_parts.append(entry_text[:500])  # Additional length limit
            total_tokens += entry_tokens
            
            evidence.append({
                "id": entry["id"],
                "date": date_str,
                "content": entry["content"][:200] + "..." if len(entry["content"]) > 200 else entry["content"],
                "mood": entry.get("mood"),
                "score": entry.get("score", 0)
            })
        
        if not context_parts:
            answer = "I couldn't find relevant journal entries to answer that question."
            return {**state, "answer": answer, "evidence": []}
        
        context = "\n\n".join(context_parts)
        
        # Build prompt based on intent with safety instructions
        safety_instruction = ""
        if low_confidence:
            safety_instruction = "\n\nIMPORTANT: The retrieved entries have low relevance. Be conservative and only state what is clearly supported by the evidence. Do not make assumptions."
        
        if intent == "reflection":
            system_prompt = f"""You are a reflective AI assistant helping someone understand their own experiences.
            Based ONLY on the journal entries provided, help them reflect on their question.
            Be empathetic, evidence-based, and never make assumptions beyond what's in the entries.
            Never invent emotional causes or reasons that aren't explicitly stated.
            Reference specific entries when relevant.{safety_instruction}"""
        elif intent == "pattern":
            system_prompt = f"""You are analyzing patterns in someone's journal entries.
            Identify patterns based ONLY on the provided entries.
            Reference specific dates and entries when describing patterns.{safety_instruction}"""
        elif intent == "temporal_comparison":
            system_prompt = f"""You are comparing different time periods in someone's life based on their journals.
            Compare ONLY based on the provided entries.
            Be specific about differences and reference entries.{safety_instruction}"""
        elif intent == "advice":
            system_prompt = f"""You are providing grounded advice based on someone's journal history.
            Give advice ONLY based on patterns and evidence from their entries.
            Never give generic life advice - only insights derived from their own data.{safety_instruction}"""
        else:  # recall
            system_prompt = f"""You are helping someone recall specific memories from their journal.
            Based ONLY on the provided entries, answer their question.
            Be specific about dates and details from the entries.{safety_instruction}"""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""User's question: {query}

Journal entries:
{context}

Please provide a thoughtful, evidence-based answer. Reference specific entries when relevant.""")
        ])
        
        # Add temporal patterns if available
        if patterns and intent in ["pattern", "temporal_comparison"]:
            patterns_text = f"\n\nTemporal patterns detected:\n{patterns}"
            prompt.messages[-1].content += patterns_text
        
        answer = await self._invoke_llm(prompt.format_messages())
        
        # Router always returns a string (never None)
        # If it's a fallback message, enhance it with context
        if "I'm having trouble" in answer:
            logger.warning("LLM returned fallback message, using enhanced safe response")
            answer = (
                "I don't have enough information from your journal entries to answer this safely. "
                "Please try again later or write more entries related to this topic."
            )
        
        llm_provider = get_llm_provider()
        logger.info(f"Generated answer using {len(evidence)} evidence entries, provider: {llm_provider}")
        
        return {**state, "answer": answer, "evidence": evidence, "llm_provider": llm_provider}
    
    async def process_query(self, user_id: str, query: str) -> Dict:
        """
        Process a memory query through the full graph.
        
        Args:
            user_id: User ID
            query: User's question
            
        Returns:
            Dict: Final answer with evidence
        """
        initial_state: GraphState = {
            "user_id": user_id,
            "query": query,
            "intent": None,
            "retrieved_entries": [],
            "temporal_patterns": None,
            "answer": None,
            "evidence": [],
            "llm_provider": None,
            "safety_check_passed": False
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        
        return {
            "answer": final_state["answer"],
            "evidence": final_state["evidence"],
            "intent": final_state["intent"],
            "retrieved_count": len(final_state["retrieved_entries"]),
            "llm_provider": final_state.get("llm_provider", "unknown")
        }


def get_memory_graph() -> MemoryGraph:
    """Get or create memory graph instance."""
    return MemoryGraph()
