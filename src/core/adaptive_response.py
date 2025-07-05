"""
Adaptive response generation functions for the Adaptive Learning System.
"""

import logging
from typing import Dict, Any, List
from langsmith import traceable

logger = logging.getLogger(__name__)


@traceable(name="generate_adaptive_response")
def generate_adaptive_response(
    collection, question: str, preferred_format: str, groq_client=None
) -> str:
    """
    Generate adaptive educational response based on user's specific question.

    Uses question analysis, semantic search with re-ranking, and Groq LLM
    to create personalized content adapted to the user's knowledge level.

    Args:
        collection: ChromaDB collection for content search
        question (str): User's specific question
        preferred_format (str): User's preferred content format
        groq_client: Groq client instance

    Returns:
        str: Generated adaptive educational response
    """
    if not groq_client:
        return "🤖 Desculpe, o serviço de IA não está configurado. Verifique as chaves de API."

    try:
        # Import required modules
        from core.question_analysis import (
            check_question_scope,
            classify_question_type,
            analyze_question_maturity,
        )
        from core.search import search_and_rerank

        # First, check if question is within scope of indexed content
        scope_validation = check_question_scope(question, collection, groq_client)

        # If question is out of scope, return limitation message
        if not scope_validation.get("in_scope", True):
            logger.info(
                f"Question out of scope: {scope_validation.get('reasoning', 'Unknown reason')}"
            )
            return generate_out_of_scope_response(question, collection, groq_client)

        # Classify question type to determine appropriate response style
        question_type = classify_question_type(question, groq_client)

        # Analyze question maturity and topics
        analysis = analyze_question_maturity(question, groq_client)
        if not analysis:
            return "🤖 Desculpe, tive um problema ao analisar sua pergunta. A IA parece estar indisponível. Por favor, tente novamente em breve."

        # Search for relevant content using the question and identified topics
        search_queries = [question] + analysis["topics"]
        all_results = []

        for query in search_queries[:3]:  # Limit to avoid too many searches
            results = search_and_rerank(collection, query, 5, 3)
            all_results.extend(results)

        # Remove duplicates
        unique_results = []
        seen_content = set()
        for result in all_results:
            content_hash = hash(
                result["content"][:100]
            )  # Use first 100 chars as identifier
            if content_hash not in seen_content:
                unique_results.append(result)
                seen_content.add(content_hash)

        # Take top results
        top_results = unique_results[:3]

        # Prepare context from best results
        context = "\n\n".join(
            [
                f"Source: {doc['metadata'].get('file', 'Unknown')}\nContent: {doc['content'][:400]}"
                for doc in top_results
            ]
        )

        # Format preference instructions
        format_instruction = {
            "text": "Provide a clear text explanation with examples.",
            "video": "Explain as if creating a video tutorial, with step-by-step guidance.",
            "exercises": "Include practical exercises and hands-on examples.",
            "mixed": "Use a combination of explanation, examples, and practical exercises.",
        }.get(preferred_format, "Provide a comprehensive explanation.")

        # Create adaptive instructions based on question type
        verbosity_instruction = {
            "concise": "Seja direto e objetivo. Evite explicações longas.",
            "moderate": "Forneça uma explicação equilibrada com exemplos práticos.",
            "detailed": "Explique detalhadamente com múltiplos exemplos e exercícios práticos.",
        }.get(
            question_type.get("verbosity", "moderate"),
            "Forneça uma explicação equilibrada.",
        )

        style_instruction = {
            "list": "Responda em formato de lista clara e organizada.",
            "conversational": "Use um tom conversacional e amigável.",
            "educational": "Use abordagem educacional com conceitos e exemplos.",
            "tutorial": "Forneça um tutorial passo-a-passo detalhado.",
        }.get(
            question_type.get("style", "educational"),
            "Use abordagem educacional com conceitos e exemplos.",
        )

        prompt = f"""
        User Question: "{question}"
        
        Question Classification:
        - Type: {question_type.get('type', 'technical')}
        - Verbosity: {question_type.get('verbosity', 'moderate')}
        - Style: {question_type.get('style', 'educational')}
        
        Question Analysis:
        - Knowledge Level: {analysis['knowledge_level']}
        - Topics: {', '.join(analysis['topics'])}
        - Confidence: {analysis['confidence']}
        
        User Preference: {preferred_format}
        
        Available Context from Educational Materials:
        {context}
        
        Instructions:
        1. {format_instruction}
        2. {verbosity_instruction}
        3. {style_instruction}
        4. Adapt complexity to {analysis['knowledge_level']} level
        5. Focus on the specific topics: {', '.join(analysis['topics'])}
        6. Use the provided context as reference material
        7. Be practical and include examples when appropriate for the question type
        8. If context is insufficient, clearly state limitations
        """

        logger.info(
            f"Generating adaptive response for {analysis['knowledge_level']} level question..."
        )
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert programming educator who adapts content to user knowledge levels and preferences.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.1,
        )
        logger.info("Successfully generated adaptive response")
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Error generating adaptive response: {e}")
        return "🤖 Desculpe, tive um problema ao gerar sua resposta. A IA parece estar indisponível. Por favor, tente novamente em breve."


@traceable(name="generate_out_of_scope_response")
def generate_out_of_scope_response(question: str, collection, groq_client=None) -> str:
    """
    Generate a helpful response when the question is outside the indexed content scope.

    Args:
        question (str): User's question that is out of scope
        collection: ChromaDB collection to analyze for scope
        groq_client: Groq client instance

    Returns:
        str: Polite response explaining the limitation with content analysis
    """
    from core.question_analysis import analyze_indexed_content

    # Get analysis of what content is actually available
    content_analysis = analyze_indexed_content(collection, groq_client)

    # Build dynamic content description
    summary = content_analysis.get("summary", "Conteúdo educacional")
    technologies = content_analysis.get("technologies", [])
    topics = content_analysis.get("topics", [])
    content_types = content_analysis.get("content_types", [])
    example_questions = content_analysis.get("example_questions", [])
    file_count = content_analysis.get("file_count", 0)

    # Format sections
    technologies_text = (
        f"- 💻 **Tecnologias:** {', '.join(technologies)}\n" if technologies else ""
    )
    topics_text = f"- 📚 **Tópicos:** {', '.join(topics)}\n" if topics else ""
    content_types_text = (
        f"- 📖 **Formatos:** {', '.join(content_types)}\n" if content_types else ""
    )
    file_info = f"- 📁 **Documentos indexados:** {file_count}\n"

    # Format example questions
    examples_text = (
        "\n".join([f'- "{q}"' for q in example_questions[:4]])
        if example_questions
        else '- "Explique os conceitos disponíveis na base de conhecimento"'
    )

    return f"""
🤖 **Desculpe, sua pergunta está fora do escopo da nossa base de conhecimento atual.**

**Sua pergunta:** "{question}"

**📋 Nossa base de conhecimento atual:**
{summary}

**🔍 Detalhes do conteúdo disponível:**
{technologies_text}{topics_text}{content_types_text}{file_info}

**💡 Sugestões de perguntas que posso responder:**
{examples_text}

**✨ Dica:** Faça perguntas relacionadas ao conteúdo que temos indexado e eu poderei gerar respostas personalizadas com texto, áudio e vídeo!

Estou aqui para ajudar! 😊
    """


@traceable(name="generate_template_content")
def generate_template_content(assessment: Dict[str, Any]) -> str:
    """
    Generate template-based educational content as fallback.

    Provides predefined educational content for each programming topic
    when Groq LLM is not available or fails to generate content.

    Args:
        assessment (Dict): User assessment results

    Returns:
        str: Template-based educational content
    """
    templates = {
        "variables": "Variables are containers for data. Example: name = 'John'",
        "data_structures": "Lists: [1,2,3], Dictionaries: {'key': 'value'}",
        "control_structures": "if/else for decisions, for/while for repetition",
        "functions": "def my_function(): return 'result'",
        "oop": "Classes group related data and behaviors together",
    }

    content = []
    knowledge_gaps = assessment.get("knowledge_gaps", [])

    for gap in knowledge_gaps:
        if gap in templates:
            content.append(f"📚 {gap.upper()}: {templates[gap]}")

    logger.info(f"Generated template content for {len(content)} knowledge gaps")
    return "\n\n".join(content) if content else "Keep practicing the fundamentals!"
