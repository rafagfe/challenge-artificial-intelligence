"""
Question analysis functions for the Adaptive Learning System.
"""

import json
import logging
from typing import Dict, Any, Optional
from langsmith import traceable

logger = logging.getLogger(__name__)


@traceable(name="analyze_question_maturity")
def analyze_question_maturity(question: str, groq_client=None) -> Dict[str, Any]:
    """
    Analyze the maturity level and topics of a user's question.

    Args:
        question (str): User's question or query
        groq_client: Groq client instance

    Returns:
        Dict[str, Any]: Analysis results including level, topics, and confidence
    """
    if not groq_client:
        logger.warning("Groq client not available, using basic classification")
        return {
            "knowledge_level": "intermediate",
            "topics": ["general"],
            "confidence": 0.5,
            "reasoning": "Default classification due to unavailable AI analysis",
        }

    analysis_prompt = f"""
    Analyze this programming question and determine:
    1. Knowledge level: beginner, intermediate, or advanced
    2. Main topics covered (list)
    3. Confidence in assessment (0-1)
    4. Brief reasoning
    
    Question: "{question}"
    
    Respond in JSON format:
    {{
        "knowledge_level": "beginner/intermediate/advanced",
        "topics": ["topic1", "topic2"],
        "confidence": 0.0-1.0,
        "reasoning": "brief explanation"
    }}
    """

    try:
        logger.info("Analyzing question maturity with Groq...")
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in assessing programming knowledge levels. Always respond with valid JSON.",
                },
                {"role": "user", "content": analysis_prompt},
            ],
            max_tokens=300,
            temperature=0.2,
        )

        analysis_text = response.choices[0].message.content
        # Try to extract JSON from response
        import re

        json_match = re.search(r"\{.*\}", analysis_text, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group())
            logger.info(
                f"Question analysis completed: {analysis['knowledge_level']} level"
            )
            return analysis
        else:
            raise ValueError("No valid JSON found in response")

    except Exception as e:
        logger.error(f"Error analyzing question: {e}")
        return {
            "knowledge_level": "intermediate",
            "topics": ["general"],
            "confidence": 0.3,
            "reasoning": f"Analysis failed: {str(e)}",
        }


@traceable(name="classify_question_type")
def classify_question_type(question: str, groq_client=None) -> Dict[str, Any]:
    """
    Classify the type of question to determine appropriate response verbosity and style.

    Args:
        question (str): User's question
        groq_client: Groq client instance

    Returns:
        Dict[str, Any]: Question classification with response guidelines
    """
    if not groq_client:
        return {"type": "technical", "verbosity": "detailed", "style": "educational"}

    try:
        classification_prompt = f"""
        Classifique o tipo da pergunta do usuário para determinar o estilo de resposta adequado.
        
        PERGUNTA: "{question}"
        
        Tipos de pergunta:
        - "scope": Pergunta sobre o que pode ser discutido/ensinado
        - "overview": Pergunta geral sobre um tópico
        - "technical": Pergunta específica/técnica
        - "guidance": Pergunta sobre como começar/estudar
        
        Responda em JSON:
        {{
            "type": "scope/overview/technical/guidance",
            "verbosity": "concise/moderate/detailed",
            "style": "list/conversational/educational/tutorial",
            "reasoning": "explicação breve da classificação"
        }}
        """

        logger.info("Classifying question type...")
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em classificação de perguntas educacionais. Responda sempre com JSON válido.",
                },
                {"role": "user", "content": classification_prompt},
            ],
            max_tokens=200,
            temperature=0.1,
        )

        classification_text = response.choices[0].message.content

        # Extract JSON from response
        import re

        json_match = re.search(r"\{.*\}", classification_text, re.DOTALL)
        if json_match:
            classification = json.loads(json_match.group())
            logger.info(
                f"Question classified as: {classification.get('type')} with {classification.get('verbosity')} verbosity"
            )
            return classification
        else:
            raise ValueError("No valid JSON found in classification response")

    except Exception as e:
        logger.error(f"Error classifying question: {e}")
        return {
            "type": "technical",
            "verbosity": "moderate",
            "style": "educational",
            "reasoning": "Classification failed, using default",
        }


@traceable(name="check_question_scope")
def check_question_scope(question: str, collection, groq_client=None) -> Dict[str, Any]:
    """
    Check if the user's question is within the scope of indexed content.

    Args:
        question (str): User's question
        collection: ChromaDB collection for content search
        groq_client: Groq client instance

    Returns:
        Dict[str, Any]: Scope validation results
    """
    if not groq_client:
        # If no LLM available, assume question is in scope
        return {
            "in_scope": True,
            "confidence": 0.5,
            "reasoning": "No LLM available for scope validation",
        }

    # First, search for related content in our indexed database
    from core.search import search_content

    search_results = search_content(collection, question, 5)

    # If no results found, it's likely out of scope
    if not search_results:
        return {
            "in_scope": False,
            "confidence": 0.9,
            "reasoning": "No related content found in indexed database",
        }

    # Extract topics from search results
    indexed_topics = set()
    for result in search_results:
        content_type = result["metadata"].get("type", "")
        file_name = result["metadata"].get("file", "")
        content_preview = result["content"][:200]

        # Add content indicators
        if "html" in content_preview.lower() or "html" in file_name.lower():
            indexed_topics.add("HTML")
        if "css" in content_preview.lower() or "css" in file_name.lower():
            indexed_topics.add("CSS")
        if "javascript" in content_preview.lower() or "js" in file_name.lower():
            indexed_topics.add("JavaScript")
        if "php" in content_preview.lower() or "php" in file_name.lower():
            indexed_topics.add("PHP")
        if (
            "programação" in content_preview.lower()
            or "programming" in content_preview.lower()
        ):
            indexed_topics.add("Programming Basics")

    # Use LLM to validate if question is within scope
    scope_prompt = f"""
    Analise se a seguinte pergunta está dentro do escopo da base de conhecimento.
    
    PERGUNTA: "{question}"
    
    ESCOPO DISPONÍVEL:
    - Tópicos: {', '.join(indexed_topics) if indexed_topics else 'Fundamentos de programação'}
    - Conteúdo: Textos, PDFs, vídeos sobre programação
    
    Responda em JSON:
    {{
        "in_scope": true/false,
        "confidence": 0.0-1.0,
        "reasoning": "explicação breve"
    }}
    """

    try:
        logger.info("Checking question scope with LLM...")
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em validação de escopo. Responda sempre com JSON válido.",
                },
                {"role": "user", "content": scope_prompt},
            ],
            max_tokens=200,
            temperature=0.1,
        )

        scope_text = response.choices[0].message.content
        # Extract JSON from response
        import re

        json_match = re.search(r"\{.*\}", scope_text, re.DOTALL)
        if json_match:
            scope_result = json.loads(json_match.group())
            logger.info(f"Scope validation: {scope_result}")
            return scope_result
        else:
            raise ValueError("No valid JSON found in scope response")

    except Exception as e:
        logger.error(f"Error in scope validation: {e}")
        return {
            "in_scope": True,
            "confidence": 0.3,
            "reasoning": "Scope validation failed, defaulting to in-scope",
        }


@traceable(name="analyze_indexed_content")
def analyze_indexed_content(collection, groq_client=None) -> Dict[str, Any]:
    """
    Analyze the indexed content using LLM to understand available topics and scope.

    Args:
        collection: ChromaDB collection containing indexed content
        groq_client: Groq client instance

    Returns:
        Dict[str, Any]: LLM analysis of available content and scope
    """
    if not groq_client:
        logger.warning("No LLM available for content analysis")
        return {
            "summary": "Conteúdo educacional disponível",
            "technologies": ["Programação"],
            "topics": ["Conceitos básicos"],
            "content_types": ["Materiais educacionais"],
            "example_questions": ["O que você pode me ensinar?"],
            "file_count": 0,
        }

    try:
        # Get sample of documents for analysis
        sample_results = collection.get(limit=30)  # Representative sample

        if not sample_results or not sample_results.get("documents"):
            return {
                "summary": "Base de conhecimento vazia",
                "technologies": [],
                "topics": [],
                "content_types": [],
                "example_questions": ["Nenhum conteúdo disponível no momento"],
                "file_count": 0,
            }

        documents = sample_results["documents"]
        metadatas = sample_results.get("metadatas", [])
        file_count = len(documents)

        # Prepare content samples for LLM analysis
        content_samples = []

        for i, (doc, meta) in enumerate(
            zip(documents[:10], metadatas[:10])
        ):  # Limit for token efficiency
            content_preview = doc[:200] if doc else ""  # First 200 chars
            file_info = meta.get("file", f"documento_{i}") if meta else f"documento_{i}"
            content_type = meta.get("type", "unknown") if meta else "unknown"

            content_samples.append(
                f"Arquivo: {file_info} (Tipo: {content_type})\nConteúdo: {content_preview}..."
            )

        # Create analysis prompt for LLM
        analysis_prompt = f"""
        Analise o conteúdo educacional indexado abaixo.
        
        CONTEÚDO INDEXADO ({file_count} documentos total):
        {chr(10).join(content_samples)}
        
        Responda em JSON:
        {{
            "summary": "Resumo do conteúdo",
            "technologies": ["lista de tecnologias identificadas"],
            "topics": ["lista de tópicos principais"],
            "content_types": ["tipos de materiais"],
            "example_questions": ["3 exemplos de perguntas"],
            "file_count": {file_count}
        }}
        """

        logger.info("Analyzing indexed content with LLM...")
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em análise de conteúdo educacional. Responda sempre com JSON válido.",
                },
                {"role": "user", "content": analysis_prompt},
            ],
            max_tokens=600,
            temperature=0.1,
        )

        analysis_text = response.choices[0].message.content

        # Extract JSON from response
        import re

        json_match = re.search(r"\{.*\}", analysis_text, re.DOTALL)
        if json_match:
            analysis_result = json.loads(json_match.group())
            logger.info(
                f"Content analysis completed: {len(analysis_result.get('technologies', []))} technologies identified"
            )
            return analysis_result
        else:
            raise ValueError("No valid JSON found in LLM analysis response")

    except Exception as e:
        logger.error(f"Error in LLM content analysis: {e}")
        return {
            "summary": "Conteúdo educacional sobre programação",
            "technologies": ["Programação geral"],
            "topics": ["Conceitos básicos"],
            "content_types": ["Materiais educacionais"],
            "example_questions": ["Explique conceitos básicos de programação"],
            "file_count": file_count if "file_count" in locals() else 0,
        }
