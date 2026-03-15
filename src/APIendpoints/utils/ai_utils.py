"""AI and LLM utilities for the backend

Integrates with local LLM running via Ollama.
Requires: ollama pull qwen2.5:3b
Run: ollama serve (on localhost:11434)
"""
import logging
import json
import requests
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:3b"
REQUEST_TIMEOUT = 60  # seconds


def call_local_model(
    prompt: str,
    model: str = DEFAULT_MODEL,
    stream: bool = False,
    temperature: float = 0.7,
    top_k: int = 40,
    top_p: float = 0.95
) -> Optional[str]:
    """
    Call a local LLM running via Ollama.

    Args:
        prompt: The prompt/instruction to send to the model
        model: Model name (default: qwen2.5:3b)
        stream: Whether to stream response (default: False for JSON response)
        temperature: Randomness of response (0.0-1.0, default 0.7)
        top_k: Token sampling parameter (default 40)
        top_p: Nucleus sampling parameter (default 0.95)

    Returns:
        Generated text response from the model, or None if error occurs

    Example:
        >>> response = call_local_model("Explain photosynthesis briefly")
        >>> print(response)
        "Photosynthesis is the process where plants convert light energy..."
    """
    try:
        # Prepare request
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p
        }

        logger.debug(f"Calling Ollama model '{model}' with prompt: {prompt[:100]}...")

        # Make HTTP POST request
        response = requests.post(
            OLLAMA_API_URL,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )

        # Check if request was successful
        if response.status_code != 200:
            logger.error(f"Ollama API error {response.status_code}: {response.text}")
            return None

        # Parse response
        response_json = response.json()
        generated_text = response_json.get("response", "").strip()

        if not generated_text:
            logger.warning("Ollama returned empty response")
            return None

        logger.info(f"Successfully generated response from {model} ({len(generated_text)} chars)")
        return generated_text

    except requests.exceptions.ConnectionError:
        logger.error(
            f"Cannot connect to Ollama at {OLLAMA_API_URL}. "
            "Make sure Ollama is running: 'ollama serve'"
        )
        return None
    except requests.exceptions.Timeout:
        logger.error(f"Ollama request timed out after {REQUEST_TIMEOUT}s")
        return None
    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        return None


def call_local_model_with_context(
    prompt: str,
    context: str,
    model: str = DEFAULT_MODEL,
    max_context_length: int = 2000
) -> Optional[str]:
    """
    Call local model with lesson context included in prompt.

    Useful for grounding AI responses in lesson content.

    Args:
        prompt: User's request/question
        context: Lesson content to provide as context
        model: Model to use
        max_context_length: Max characters of context to include (to avoid token overflow)

    Returns:
        Generated response grounded in context
    """
    # Trim context if too long
    if len(context) > max_context_length:
        context = context[:max_context_length] + "..."

    # Build enhanced prompt with context
    enhanced_prompt = f"""Using the following lesson content, answer the user's request.

LESSON CONTENT:
{context}

USER REQUEST:
{prompt}

RESPONSE:"""

    return call_local_model(enhanced_prompt, model=model)


def generate_explanation_with_ai(
    lesson_content: str,
    user_question: str,
    model: str = DEFAULT_MODEL
) -> Optional[str]:
    """
    Generate an AI-powered explanation grounded in lesson content.

    Args:
        lesson_content: The lesson material
        user_question: Student's question about the lesson
        model: LLM to use

    Returns:
        AI-generated explanation
    """
    prompt = f"""You are an educational tutor. Based on the lesson material, provide a clear,
accessible explanation that answers the student's question. Keep explanations concise and avoid jargon.

LESSON MATERIAL:
{lesson_content[:1500]}

STUDENT QUESTION:
{user_question}

EXPLANATION:"""

    return call_local_model_with_context(prompt, lesson_content, model=model)


def generate_quiz_question_with_ai(
    lesson_content: str,
    topic: str,
    difficulty: str = "medium",
    model: str = DEFAULT_MODEL
) -> Optional[Dict[str, Any]]:
    """
    Use AI to generate a single quiz question from lesson content.

    Args:
        lesson_content: The lesson material
        topic: Topic to create question about
        difficulty: Question difficulty (easy/medium/hard)
        model: LLM to use

    Returns:
        Dict with question_text, options, correct_answer, or None if error
    """
    prompt = f"""Create a multiple choice quiz question based on this lesson material.

Difficulty: {difficulty}
Topic: {topic}

LESSON MATERIAL:
{lesson_content[:1000]}

Respond with JSON format:
{{"question_text": "...", "options": ["A", "B", "C", "D"], "correct_answer": "A"}}

QUESTION:"""

    response = call_local_model(prompt, model=model)

    if not response:
        return None

    # Try to parse JSON response
    try:
        import json
        # Extract JSON from response (model might include extra text)
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = response[start:end]
            return json.loads(json_str)
    except Exception as e:
        logger.warning(f"Failed to parse AI-generated question as JSON: {e}")
        return None

    return None


def is_ollama_available() -> bool:
    """
    Check if Ollama is running and accessible.

    Returns:
        True if Ollama is available, False otherwise
    """
    try:
        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=5
        )
        return response.status_code == 200
    except Exception:
        return False


def get_available_models() -> list:
    """
    Get list of available models in Ollama.

    Returns:
        List of model names, or empty list if Ollama unavailable
    """
    try:
        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return [m.get("name", "") for m in data.get("models", [])]
    except Exception as e:
        logger.warning(f"Could not fetch available models: {e}")

    return []


def build_quiz_generation_prompt(
    lesson_context: str,
    topic: str,
    num_questions: int = 3,
    difficulty: str = "easy",
    for_dyslexic_learners: bool = True
) -> str:
    """
    Build a structured prompt for quiz generation optimized for Ollama.

    The prompt instructs the model to:
    - Generate exactly N quiz questions (default 3)
    - Use ONLY the provided lesson context
    - Keep questions simple and accessible (for dyslexic learners)
    - Prefer multiple choice or true/false formats
    - Return valid JSON only

    Args:
        lesson_context: The lesson content to base questions on
        topic: The topic/title of the quiz
        num_questions: Number of questions to generate (default 3)
        difficulty: Question difficulty (easy/medium/hard)
        for_dyslexic_learners: If True, optimize for accessibility

    Returns:
        Structured prompt string formatted for LLM consumption
    """

    # Accessibility guidelines for dyslexic learners
    accessibility_guidelines = ""
    if for_dyslexic_learners:
        accessibility_guidelines = """
ACCESSIBILITY GUIDELINES (IMPORTANT FOR DYSLEXIC LEARNERS):
- Use SHORT, simple sentences
- Avoid complex vocabulary
- Use familiar words only
- Keep options brief (2-5 words each)
- Use sans-serif font friendly language
- One idea per question
"""

    prompt = f"""You are an educational assistant creating quiz questions.

LESSON CONTEXT:
{lesson_context}

QUIZ SPECIFICATIONS:
- Topic: {topic}
- Number of questions: {num_questions}
- Question difficulty: {difficulty}
- Question types: Multiple choice (MCQ) OR True/False ONLY
- Use ONLY information from the lesson context above
- Do NOT add information outside the context
- Do NOT make assumptions

{accessibility_guidelines}

RESPONSE FORMAT:
Return ONLY a valid JSON object (nothing else):
{{
  "quiz_id": "quiz_[topic]_[timestamp]",
  "topic": "{topic}",
  "questions": [
    {{
      "question_id": "q1",
      "type": "mcq",
      "question_text": "Clear, simple question text?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "concept_tag": "main_concept",
      "difficulty": "{difficulty}"
    }},
    {{
      "question_id": "q2",
      "type": "true_false",
      "question_text": "Statement from the lesson",
      "options": ["True", "False"],
      "correct_answer": "True",
      "concept_tag": "key_concept",
      "difficulty": "{difficulty}"
    }}
  ]
}}

Generate {num_questions} questions now:"""

    return prompt


def generate_quiz_with_ai(
    lesson_context: str,
    topic: str,
    num_questions: int = 3,
    difficulty: str = "easy",
    for_dyslexic_learners: bool = True,
    model: str = DEFAULT_MODEL
) -> Dict[str, Any]:
    """
    Generate a quiz using AI (Ollama) with structured prompts.

    Robust generation with fallback to simple quiz if AI fails.
    This function ALWAYS returns a valid quiz - never returns None.

    Args:
        lesson_context: The lesson content
        topic: Quiz topic/title
        num_questions: Number of questions to generate
        difficulty: Question difficulty level
        for_dyslexic_learners: Optimize for accessibility
        model: LLM model to use

    Returns:
        Quiz dict with quiz_id, topic, and questions array.
        Returns fallback quiz if AI fails (never returns None).
    """
    try:
        # Build structured prompt
        prompt = build_quiz_generation_prompt(
            lesson_context=lesson_context,
            topic=topic,
            num_questions=num_questions,
            difficulty=difficulty,
            for_dyslexic_learners=for_dyslexic_learners
        )

        logger.info(f"Calling AI to generate {num_questions} quiz questions for '{topic}'")

        # Call LLM
        response = call_local_model(prompt, model=model, temperature=0.5)

        # If model returned response, try to parse it
        if response:
            quiz_data = _parse_quiz_json(response)
            if quiz_data:
                logger.info(f"Successfully generated AI quiz with {len(quiz_data.get('questions', []))} questions")
                return quiz_data

        # If we get here, AI response was invalid/empty
        logger.warning(f"AI quiz generation failed or returned invalid JSON, using fallback")

    except Exception as e:
        logger.error(f"Error during AI quiz generation: {e}")

    # Fallback: return simple quiz
    logger.info(f"Returning FALLBACK quiz for topic '{topic}'")
    from utils.quiz_generator import fallback_quiz
    return fallback_quiz(topic=topic)


def _parse_quiz_json(response: str) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON from model response with robust error handling.

    The model might include extra text before/after JSON,
    so we extract the JSON block and parse it carefully.

    Args:
        response: Raw text response from the model

    Returns:
        Parsed quiz dict if successful, None if parsing fails
    """
    if not response or not isinstance(response, str):
        logger.warning("Empty or invalid response for JSON parsing")
        return None

    try:
        # Extract JSON object from response
        # Model might say "Here's your quiz:" then return JSON
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1

        if start_idx < 0 or end_idx <= start_idx:
            logger.warning("No JSON object found in response")
            return None

        json_str = response[start_idx:end_idx]

        # Parse JSON
        quiz_data = json.loads(json_str)

        # Validate structure
        if not _validate_quiz_structure(quiz_data):
            logger.error("Parsed JSON is not a valid quiz structure")
            return None

        return quiz_data

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {e}")
        logger.debug(f"Attempted to parse: {response[:300]}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing quiz JSON: {e}")
        return None


def _validate_quiz_structure(quiz_data: Any) -> bool:
    """
    Validate that parsed data matches expected quiz structure.

    Args:
        quiz_data: The parsed data to validate

    Returns:
        True if valid quiz structure, False otherwise
    """
    try:
        # Check basic structure
        if not isinstance(quiz_data, dict):
            logger.debug(f"Quiz data is not dict: {type(quiz_data)}")
            return False

        # Check required fields
        required_fields = ["quiz_id", "topic", "questions"]
        for field in required_fields:
            if field not in quiz_data:
                logger.debug(f"Missing required field: {field}")
                return False

        # Check questions is a list
        if not isinstance(quiz_data["questions"], list):
            logger.debug(f"Questions is not list: {type(quiz_data['questions'])}")
            return False

        # Check at least one question
        if len(quiz_data["questions"]) == 0:
            logger.debug("Quiz has no questions")
            return False

        # Validate each question
        for i, question in enumerate(quiz_data["questions"]):
            if not _validate_question_structure(question, i):
                return False

        return True

    except Exception as e:
        logger.error(f"Error validating quiz structure: {e}")
        return False


def _validate_question_structure(question: Any, index: int) -> bool:
    """
    Validate a single question structure.

    Args:
        question: The question to validate
        index: Question index (for logging)

    Returns:
        True if valid, False otherwise
    """
    try:
        if not isinstance(question, dict):
            logger.debug(f"Question {index} is not dict: {type(question)}")
            return False

        required_fields = ["question_id", "type", "question_text", "correct_answer"]
        for field in required_fields:
            if field not in question:
                logger.debug(f"Question {index} missing field: {field}")
                return False

        # Validate question type
        valid_types = ["mcq", "true_false", "short_answer"]
        if question["type"] not in valid_types:
            logger.debug(f"Question {index} invalid type: {question['type']}")
            return False

        # Validate options for MCQ/true_false
        if question["type"] in ["mcq", "true_false"]:
            if "options" not in question or not isinstance(question["options"], list):
                logger.debug(f"Question {index} missing/invalid options")
                return False

            if len(question["options"]) == 0:
                logger.debug(f"Question {index} has no options")
                return False

        return True

    except Exception as e:
        logger.error(f"Error validating question {index}: {e}")
        return False


def build_explanation_prompt(
    lesson_context: str,
    user_question: str,
    for_dyslexic_learners: bool = True
) -> str:
    """
    Build a structured prompt for generating explanations.

    Args:
        lesson_context: The lesson material
        user_question: Student's question
        for_dyslexic_learners: Optimize for accessibility

    Returns:
        Structured prompt for LLM
    """

    accessibility_note = ""
    if for_dyslexic_learners:
        accessibility_note = """
Remember: This explanation is for students with dyslexic learners.
- Use short, simple sentences
- Avoid jargon
- Use active voice
- Break complex ideas into small parts
"""

    prompt = f"""You are an educational tutor explaining concepts from a lesson.

LESSON MATERIAL:
{lesson_context[:1500]}

STUDENT QUESTION:
{user_question}

{accessibility_note}

INSTRUCTIONS:
- Answer ONLY based on the lesson material
- Keep explanation clear and concise
- Use simple, everyday language
- Break complex ideas into smaller parts
- Do NOT add information outside the lesson

EXPLANATION:"""

    return prompt


def build_text_simplification_prompt(
    text: str,
    for_dyslexic_learners: bool = True
) -> str:
    """
    Build a structured prompt for simplifying text.

    Args:
        text: Text to simplify
        for_dyslexic_learners: Optimize for dyslexia accessibility

    Returns:
        Structured prompt for LLM
    """

    dyslexia_guidelines = ""
    if for_dyslexic_learners:
        dyslexia_guidelines = """

DYSLEXIA-FRIENDLY SIMPLIFICATION:
- Break paragraphs into 2-3 sentences maximum
- Use short words (avoid words longer than 3 syllables where possible)
- Use sans-serif friendly vocabulary
- One idea per sentence
- Use active voice
- Number key points"""

    prompt = f"""Simplify the following text for better readability and understanding.{dyslexia_guidelines}

ORIGINAL TEXT:
{text}

SIMPLIFIED TEXT:"""

    return prompt


# ============= MOCK FUNCTIONS (for testing without Ollama) =============

def call_local_model_mock(prompt: str, **kwargs) -> str:
    """
    Mock version of call_local_model for testing without Ollama running.

    Returns plausible but generic responses.
    """
    logger.info(f"MOCK MODE: Responding to prompt (Ollama not available)")

    # Simple keyword-based mock responses
    if "photosynthesis" in prompt.lower():
        return "Photosynthesis is the process by which plants convert light energy into chemical energy, producing oxygen and glucose."
    elif "quiz" in prompt.lower() or "question" in prompt.lower():
        return '{"question_text": "What is photosynthesis?", "options": ["Energy conversion", "Respiration", "Growth", "Movement"], "correct_answer": "A"}'
    elif "explain" in prompt.lower():
        return "This topic involves fundamental concepts that are important for understanding the broader subject matter."
    else:
        return "Based on the lesson material provided, this demonstrates an important educational concept."
