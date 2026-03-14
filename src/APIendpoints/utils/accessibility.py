"""Accessibility utilities for content adaptation (dyslexia support)"""
import logging

logger = logging.getLogger(__name__)


def simplify_text(text: str, level: str = "medium") -> str:
    """
    Simplify text for better readability.

    Args:
        text: Original text
        level: Simplification level (light, medium, heavy)

    Returns:
        Simplified text
    """
    if not text:
        return text

    # Replace complex words with simpler alternatives
    word_replacements = {
        "utilize": "use",
        "facilitate": "help",
        "subsequent": "next",
        "therefore": "so",
        "furthermore": "also",
        "consequently": "so",
        "insufficient": "not enough",
        "approximately": "about",
        "particular": "special",
        "comprehensive": "complete",
        "obtain": "get",
        "accumulate": "build up",
        "demonstrate": "show",
        "constitute": "make up",
        "implement": "carry out",
        "provide": "give",
        "requires": "needs",
        "numerous": "many",
        "adequate": "enough",
    }

    simplified = text
    for complex_word, simple_word in word_replacements.items():
        # Case-insensitive replacement
        simplified = simplified.replace(complex_word, simple_word)
        simplified = simplified.replace(complex_word.capitalize(), simple_word.capitalize())
        simplified = simplified.replace(complex_word.upper(), simple_word.upper())

    if level == "heavy":
        # Additional simplification: break long sentences
        simplified = break_long_sentences(simplified)

    return simplified


def break_long_sentences(text: str, max_length: int = 80) -> str:
    """
    Break long sentences into shorter ones for better readability.

    Args:
        text: Original text
        max_length: Maximum sentence length

    Returns:
        Text with shorter sentences
    """
    sentences = text.split('. ')
    result = []

    for sentence in sentences:
        if len(sentence) > max_length and ',' in sentence:
            # Try to split on commas
            parts = sentence.split(', ')
            for i, part in enumerate(parts):
                if i < len(parts) - 1:
                    result.append(part + '.')
                else:
                    result.append(part + '.')
        else:
            result.append(sentence + '.')

    return ' '.join(result).replace('. . ', '. ')


def get_adaptation_css(support_mode: str = "dyslexia") -> dict:
    """
    Get CSS styling for accessibility adaptations.

    Args:
        support_mode: Type of support (dyslexia, visual_impairment, etc)

    Returns:
        Dict with CSS properties
    """
    if support_mode == "dyslexia":
        return {
            "font_family": "sans-serif",  # Arial, Verdana, or Helvetica
            "font_size": "18px",
            "font_weight": "400",
            "line_height": "1.8",  # Increased line spacing
            "letter_spacing": "0.12em",  # Increased letter spacing
            "word_spacing": "0.2em",
            "background_color": "#f5f5f0",  # Light cream/off-white
            "text_color": "#1a1a1a",  # Dark text
            "left_margin": "2rem",
            "right_margin": "2rem",
            "text_align": "left",
            "avoid_justified": True,
            "tab_width": "4",
            "color_contrast": "high"
        }
    elif support_mode == "visual_impairment":
        return {
            "font_size": "24px",
            "line_height": "2.0",
            "background_color": "#000000",
            "text_color": "#FFFF00",
            "letter_spacing": "0.15em",
            "font_family": "sans-serif"
        }
    else:
        # Default
        return {
            "font_family": "sans-serif",
            "font_size": "16px",
            "line_height": "1.6",
            "letter_spacing": "0.05em"
        }


def apply_accessibility_formatting(content: str, support_mode: str = "dyslexia") -> dict:
    """
    Apply comprehensive accessibility formatting.

    Args:
        content: Original content
        support_mode: Type of accessibility support

    Returns:
        Dict with formatted content and styling
    """
    # Get CSS styling
    css_styles = get_adaptation_css(support_mode)

    # Simplify text
    simplified_content = simplify_text(content, level="medium")

    # Break into smaller sections
    sections = break_into_sections(simplified_content)

    return {
        "original_content": content,
        "adapted_content": simplified_content,
        "sections": sections,
        "css_styles": css_styles,
        "support_mode": support_mode
    }


def break_into_sections(text: str, words_per_section: int = 150) -> list:
    """
    Break content into manageable sections.

    Args:
        text: Content to break
        words_per_section: Target words per section

    Returns:
        List of text sections with headers
    """
    sentences = text.split('. ')
    sections = []
    current_section = ""
    word_count = 0

    for i, sentence in enumerate(sentences):
        words_in_sentence = len(sentence.split())
        word_count += words_in_sentence

        current_section += sentence + '. '

        if word_count >= words_per_section and i < len(sentences) - 1:
            # Create a new section
            sections.append({
                "title": f"Section {len(sections) + 1}",
                "content": current_section.strip(),
                "word_count": word_count
            })
            current_section = ""
            word_count = 0

    # Add remaining content as final section
    if current_section.strip():
        sections.append({
            "title": f"Section {len(sections) + 1}",
            "content": current_section.strip(),
            "word_count": word_count
        })

    return sections


def add_visual_markers(content: str) -> str:
    """
    Add visual markers (emphasis, color coding) to content.

    Args:
        content: Original content

    Returns:
        Content with visual markers (markdown/html compatible)
    """
    marked_content = content

    # Highlight important concepts (wrapped in special markers)
    patterns = [
        (r"(definition|defined as|means):", r"🔹 \1:"),
        (r"(important|note|remember|key point):", r"⭐ \1:"),
        (r"(example|for example|instance):", r"📌 \1:"),
    ]

    for pattern, replacement in patterns:
        import re
        marked_content = re.sub(pattern, replacement, marked_content, flags=re.IGNORECASE)

    return marked_content
