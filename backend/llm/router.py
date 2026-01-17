"""
LLM Router with safe, production-ready fallback (OpenAI → Gemini → Groq).
All fallback logic is isolated here - LangGraph remains provider-agnostic.
"""

from typing import Optional, List
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
# langchain_groq removed - requires langchain-core>=0.1.41 which conflicts with langchain 0.1.6
# from langchain_groq import ChatGroq
from config.settings import get_settings
import logging

logger = logging.getLogger(__name__)


class LLMRouter:
    """
    LLM Router with safe fallback chain: OpenAI → Gemini → Groq.
    
    OpenAI is always primary (required).
    Gemini and Groq are optional fallbacks.
    All fallback logic is isolated here.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self._openai_llm: Optional[BaseChatModel] = None
        self._gemini_llm: Optional[BaseChatModel] = None
        self._groq_llm: Optional[BaseChatModel] = None
        self._last_provider: Optional[str] = None
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize all available providers at startup."""
        # OpenAI is required
        if not self.settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY must be set (OpenAI is required)")
        
        try:
            self._openai_llm = self._create_openai_llm()
            logger.info("Initialized LLM: OpenAI (gpt-4o-mini)")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI LLM: {e}") from e
        
        # Gemini is optional
        if self.settings.GEMINI_API_KEY:
            try:
                self._gemini_llm = self._create_gemini_llm()
                logger.info("Initialized LLM: Gemini (gemini-1.5-flash-002)")
            except Exception as e:
                logger.warning(f"Gemini initialization failed (will skip): {e}")
                self._gemini_llm = None
        
        # Groq is disabled - langchain-groq requires langchain-core>=0.1.41 (incompatible with langchain 0.1.6)
        # if self.settings.GROQ_API_KEY:
        #     try:
        #         self._groq_llm = self._create_groq_llm()
        #         logger.info("Initialized LLM: Groq (llama-3.3-8b-instruct)")
        #     except Exception as e:
        #         logger.warning(f"Groq initialization failed (will skip): {e}")
        #         self._groq_llm = None
        self._groq_llm = None
    
    def _create_openai_llm(self) -> BaseChatModel:
        """Create OpenAI LLM instance with approved model."""
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=self.settings.LLM_TEMPERATURE,
            api_key=self.settings.OPENAI_API_KEY
        )
    
    def _create_gemini_llm(self) -> BaseChatModel:
        """Create Gemini LLM instance with approved model."""
        # Use gemini-1.5-flash-002 (stable, not v1beta)
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-002",
            temperature=self.settings.LLM_TEMPERATURE,
            google_api_key=self.settings.GEMINI_API_KEY
        )
    
    # def _create_groq_llm(self) -> BaseChatModel:
    #     """Create Groq LLM instance with approved model."""
    #     # Disabled: langchain-groq requires langchain-core>=0.1.41 (incompatible with langchain 0.1.6)
    #     # Use llama-3.3-8b-instruct (current, not decommissioned)
    #     return ChatGroq(
    #         model="llama-3.3-8b-instruct",
    #         temperature=self.settings.LLM_TEMPERATURE,
    #         groq_api_key=self.settings.GROQ_API_KEY
    #     )
    
    async def generate(self, messages: List[BaseMessage]) -> str:
        """
        Generate response with automatic fallback.
        
        Tries providers in order: OpenAI → Gemini → Groq
        Returns first successful response or safe fallback string.
        
        Args:
            messages: List of LangChain message objects
            
        Returns:
            str: LLM response or safe fallback message
        """
        # Try OpenAI first (required)
        try:
            response = await self._openai_llm.ainvoke(messages)
            self._last_provider = "openai"
            return response.content
        except Exception as e:
            logger.warning(f"OpenAI call failed: {str(e)}")
            # Continue to fallback
        
        # Try Gemini (optional fallback)
        if self._gemini_llm is not None:
            try:
                logger.info("Attempting Gemini fallback...")
                response = await self._gemini_llm.ainvoke(messages)
                self._last_provider = "gemini"
                logger.info("Gemini fallback successful")
                return response.content
            except Exception as e:
                logger.warning(f"Gemini fallback failed: {str(e)}")
                # Continue to next fallback
        
        # Try Groq (last resort fallback)
        if self._groq_llm is not None:
            try:
                logger.info("Attempting Groq fallback...")
                response = await self._groq_llm.ainvoke(messages)
                self._last_provider = "groq"
                logger.info("Groq fallback successful")
                return response.content
            except Exception as e:
                logger.warning(f"Groq fallback failed: {str(e)}")
        
        # All providers failed - return safe fallback
        logger.error("All LLM providers failed. Returning safe fallback message.")
        self._last_provider = "fallback"
        return "I'm having trouble answering right now. Please try again in a moment."
    
    def get_provider(self) -> str:
        """Get the last used provider name for logging."""
        return self._last_provider or "openai"
    
    def is_available(self) -> bool:
        """Check if at least one provider is available."""
        return self._openai_llm is not None


# Global router instance
_router: Optional[LLMRouter] = None


def get_router() -> LLMRouter:
    """Get or create router instance."""
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router


def get_llm() -> BaseChatModel:
    """
    Get LLM instance (for backward compatibility).
    Returns OpenAI LLM as primary.
    """
    router = get_router()
    if router._openai_llm is None:
        raise RuntimeError("LLM not initialized")
    return router._openai_llm


def get_llm_provider() -> str:
    """Get the current LLM provider name for logging."""
    return get_router().get_provider()


async def generate_with_fallback(messages: List[BaseMessage]) -> str:
    """
    Generate LLM response with automatic fallback.
    This is the main entry point for LangGraph.
    
    Args:
        messages: List of LangChain message objects
        
    Returns:
        str: LLM response or safe fallback message
    """
    router = get_router()
    return await router.generate(messages)
