"""
Hybrid retrieval system with temporal and mood weighting.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import asyncpg
from database.connection import get_db_pool
from embeddings.embedder import get_embedder
import numpy as np
from math import exp


class HybridRetriever:
    """Hybrid retriever with vector similarity, temporal, and mood weighting."""
    
    def __init__(self):
        self.embedder = get_embedder()
        self.embedding_dim = self.embedder.get_dimension()
    
    async def retrieve(
        self,
        user_id: str,
        query: str,
        query_embedding: Optional[List[float]] = None,
        limit: int = 10,
        time_filter: Optional[Dict] = None,
        mood_filter: Optional[str] = None,
        recency_weight: float = 0.3,
        mood_weight: float = 0.2
    ) -> List[Dict]:
        """
        Retrieve relevant journal entries using hybrid approach.
        
        Args:
            user_id: User ID for strict isolation
            query: User's query text
            query_embedding: Pre-computed query embedding (optional)
            limit: Maximum number of results
            time_filter: Dict with 'start_date' and/or 'end_date' (ISO format)
            mood_filter: Mood to filter or weight by
            recency_weight: Weight for recency scoring (0-1)
            mood_weight: Weight for mood matching (0-1)
            
        Returns:
            List[Dict]: Retrieved journal entries with scores
        """
        pool = await get_db_pool()
        
        # Generate query embedding if not provided
        if query_embedding is None:
            query_embedding = await self.embedder.embed_text(query)
        
        # Build SQL query with filters
        # Only use journal_embeddings (derived data) - ensures we use latest embeddings only
        base_query = """
            SELECT 
                j.id,
                j.user_id,
                j.content,
                j.mood,
                j.entry_date,
                j.created_at,
                je.embedding,
                je.metadata
            FROM journal_embeddings je
            INNER JOIN journals j ON j.id = je.journal_id
            WHERE je.user_id = $1
        """
        
        params = [user_id]
        param_idx = 2
        
        # Add time filters (use entry_date for date-based filtering)
        if time_filter:
            if "start_date" in time_filter:
                base_query += f" AND je.entry_date >= ${param_idx}::date"
                # Convert ISO string to date if needed
                start_date = time_filter["start_date"]
                if isinstance(start_date, str):
                    from datetime import datetime
                    start_date = datetime.fromisoformat(start_date.split('T')[0]).date()
                params.append(start_date)
                param_idx += 1
            if "end_date" in time_filter:
                base_query += f" AND je.entry_date <= ${param_idx}::date"
                # Convert ISO string to date if needed
                end_date = time_filter["end_date"]
                if isinstance(end_date, str):
                    from datetime import datetime
                    end_date = datetime.fromisoformat(end_date.split('T')[0]).date()
                params.append(end_date)
                param_idx += 1
        
        # Add mood filter if specified
        if mood_filter:
            base_query += f" AND j.mood = ${param_idx}"
            params.append(mood_filter)
            param_idx += 1
        
        # Ensure we have embeddings
        base_query += " AND je.embedding IS NOT NULL"
        
        # Order by similarity first (we'll re-rank)
        # Fix: Use correct parameter syntax - asyncpg uses $1, $2, etc.
        # Convert embedding list to string format for pgvector (same as storage)
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        base_query += f"""
            ORDER BY je.embedding <=> ${param_idx}::vector
            LIMIT ${param_idx + 1}
        """
        params.append(embedding_str)  # Pass as string (same format as storage)
        params.append(limit * 3)  # Get more candidates for re-ranking
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(base_query, *params)
        
        # Re-rank with temporal and mood weighting
        scored_results = []
        now = datetime.now(datetime.now().astimezone().tzinfo)
        
        for row in rows:
            # Vector similarity score (cosine similarity, higher is better)
            if row['embedding']:
                vec_sim = self._cosine_similarity(query_embedding, row['embedding'])
            else:
                vec_sim = 0.0
            
            # Temporal recency score (use entry_date for recency calculation)
            entry_date = row.get('entry_date')
            if entry_date:
                if isinstance(entry_date, str):
                    entry_date = datetime.fromisoformat(entry_date.split('T')[0]).date()
                elif hasattr(entry_date, 'date'):
                    entry_date = entry_date.date() if hasattr(entry_date, 'date') else entry_date
                days_ago = (now.date() - entry_date).days
            else:
                # Fallback to created_at if entry_date not available
                created_at = row['created_at']
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_ago = (now - created_at).days
            
            recency_score = exp(-days_ago / 30.0)  # Exponential decay over 30 days
            
            # Mood matching score
            mood_score = 1.0
            if mood_filter and row['mood']:
                mood_score = 2.0 if row['mood'].lower() == mood_filter.lower() else 0.5
            
            # Combined score
            final_score = (
                (1 - recency_weight - mood_weight) * vec_sim +
                recency_weight * recency_score +
                mood_weight * mood_score
            )
            
            # Use entry_date for date display
            entry_date = row.get('entry_date')
            if entry_date:
                if hasattr(entry_date, 'isoformat'):
                    date_str = entry_date.isoformat()
                elif hasattr(entry_date, 'date'):
                    date_str = entry_date.date().isoformat()
                else:
                    date_str = str(entry_date)
            else:
                # Fallback to created_at if entry_date not available
                created_at = row['created_at']
                date_str = created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)
            
            scored_results.append({
                "id": str(row['id']),
                "user_id": str(row['user_id']),
                "content": row['content'],
                "mood": row['mood'],
                "entry_date": date_str,
                "created_at": row['created_at'].isoformat() if hasattr(row['created_at'], 'isoformat') else str(row['created_at']),
                "metadata": row['metadata'] or {},
                "score": final_score,
                "vector_sim": vec_sim,
                "recency_score": recency_score,
                "mood_score": mood_score
            })
        
        # Sort by final score and return top results
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        return scored_results[:limit]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot_product / (norm1 * norm2))
    
    async def extract_temporal_filters(self, query: str) -> Optional[Dict]:
        """
        Extract temporal filters from query text.
        
        Args:
            query: User query text
            
        Returns:
            Optional[Dict]: Dict with 'start_date' and/or 'end_date' if found
        """
        query_lower = query.lower()
        now = datetime.now()
        
        # Simple keyword-based extraction (can be enhanced with NLP)
        filters = {}
        
        # Month names
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        for month_name, month_num in months.items():
            if month_name in query_lower:
                year = now.year
                # Check if year is mentioned
                if str(year) in query or str(year - 1) in query:
                    if str(year - 1) in query:
                        year = year - 1
                
                start = datetime(year, month_num, 1)
                if month_num == 12:
                    end = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end = datetime(year, month_num + 1, 1) - timedelta(days=1)
                
                filters['start_date'] = start.isoformat()
                filters['end_date'] = end.isoformat()
                return filters
        
        # "Last week", "last month", etc.
        if 'last week' in query_lower:
            end = now
            start = now - timedelta(days=7)
            filters['start_date'] = start.isoformat()
            filters['end_date'] = end.isoformat()
            return filters
        
        if 'last month' in query_lower:
            end = now
            start = now - timedelta(days=30)
            filters['start_date'] = start.isoformat()
            filters['end_date'] = end.isoformat()
            return filters
        
        return None
    
    async def extract_mood_filter(self, query: str) -> Optional[str]:
        """
        Extract mood filter from query text.
        
        Args:
            query: User query text
            
        Returns:
            Optional[str]: Mood string if found
        """
        query_lower = query.lower()
        
        # Mood keywords
        mood_keywords = {
            'anxious': 'anxious',
            'anxiety': 'anxious',
            'happy': 'happy',
            'sad': 'sad',
            'depressed': 'sad',
            'angry': 'angry',
            'frustrated': 'angry',
            'excited': 'excited',
            'calm': 'calm',
            'stressed': 'stressed',
            'burned out': 'burned_out',
            'burnout': 'burned_out',
            'grateful': 'grateful',
            'gratitude': 'grateful'
        }
        
        for keyword, mood in mood_keywords.items():
            if keyword in query_lower:
                return mood
        
        return None


def get_retriever() -> HybridRetriever:
    """Get or create retriever instance."""
    return HybridRetriever()

