"""
Search and reranking functions for the Adaptive Learning System.
"""
import logging
from typing import List, Dict, Any
from langsmith import traceable

logger = logging.getLogger(__name__)


@traceable(name="search_content")
def search_content(collection, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search for relevant content in ChromaDB using semantic similarity.
    
    Performs vector similarity search to find the most relevant documents
    based on the user's query or identified knowledge gaps.
    
    Args:
        collection: ChromaDB collection instance
        query (str): Search query or topic
        n_results (int): Number of results to return (default: 3)
        
    Returns:
        List[Dict[str, Any]]: List of relevant documents with content and metadata
    """
    try:
        results = collection.query(query_texts=[query], n_results=n_results)
        
        docs = []
        for i in range(len(results['documents'][0])):
            docs.append({
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i]
            })
        
        logger.info(f"Found {len(docs)} relevant documents for query: '{query}'")
        return docs
    except Exception as e:
        logger.error(f"Error searching content: {e}")
        return []


@traceable(name="rerank_results")
def rerank_results(query: str, initial_results: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Re-rank search results using additional relevance scoring.
    
    Applies keyword matching and content type preferences to improve
    the relevance of initial semantic search results.
    
    Args:
        query (str): Original search query
        initial_results (List[Dict]): Initial ChromaDB search results
        top_k (int): Number of top results to return
        
    Returns:
        List[Dict[str, Any]]: Re-ranked results with improved relevance
    """
    if not initial_results:
        return []
    
    query_terms = set(query.lower().split())
    
    # Calculate enhanced relevance scores
    enhanced_results = []
    for result in initial_results:
        content = result['content'].lower()
        metadata = result['metadata']
        
        # Base semantic similarity (assume 0.8 if not provided)
        base_score = 0.8
        
        # Keyword overlap bonus
        content_terms = set(content.split())
        overlap = len(query_terms.intersection(content_terms))
        keyword_bonus = min(overlap * 0.1, 0.3)
        
        # Content type preferences
        type_bonus = 0.0
        content_type = metadata.get('type', '')
        if content_type == 'exercise' and any(term in query.lower() for term in ['exercise', 'practice', 'question']):
            type_bonus = 0.2
        elif content_type == 'video' and any(term in query.lower() for term in ['video', 'watch', 'tutorial']):
            type_bonus = 0.2
        elif content_type == 'text' and any(term in query.lower() for term in ['explain', 'definition', 'concept']):
            type_bonus = 0.1
        
        # Final relevance score
        final_score = base_score + keyword_bonus + type_bonus
        
        enhanced_results.append({
            **result,
            'relevance_score': final_score,
            'keyword_matches': overlap
        })
    
    # Sort by relevance score and return top results
    enhanced_results.sort(key=lambda x: x['relevance_score'], reverse=True)
    logger.info(f"Re-ranked {len(initial_results)} results, returning top {top_k}")
    
    return enhanced_results[:top_k]


def search_and_rerank(collection, query: str, n_results: int = 5, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Combined search and rerank function.
    
    Args:
        collection: ChromaDB collection instance
        query (str): Search query
        n_results (int): Initial number of results to retrieve
        top_k (int): Final number of results to return
        
    Returns:
        List[Dict[str, Any]]: Reranked search results
    """
    # First search
    initial_results = search_content(collection, query, n_results)
    
    # Then rerank
    if initial_results:
        return rerank_results(query, initial_results, top_k)
    else:
        return [] 