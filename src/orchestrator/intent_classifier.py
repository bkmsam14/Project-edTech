"""
Intent Classifier

Detects user intent from natural language requests.
For MVP, uses keyword matching. Can be upgraded to ML-based classification.
"""

import re
from typing import Dict, List, Tuple
from .schemas import Intent


class IntentClassifier:
    """Classifies user intent from natural language input"""

    def __init__(self):
        """Initialize intent classifier with keyword patterns"""
        self.intent_patterns: Dict[Intent, List[str]] = {
            Intent.EXPLAIN_LESSON: [
                r'\bexplain\b',
                r'\bwhat is\b',
                r'\bwhat are\b',
                r'\bteach me\b',
                r'\bhelp me understand\b',
                r'\bwhat does.*mean\b',
                r'\bhow does.*work\b',
                r'\bcan you explain\b',
                r'\btell me about\b',
            ],
            Intent.SIMPLIFY_CONTENT: [
                r'\bsimplify\b',
                r'\beasier\b',
                r'\bsimpler\b',
                r'\bbreak down\b',
                r'\bin simple terms\b',
                r'\bplain language\b',
                r'\beli5\b',
                r'\bmake.*easier to understand\b',
            ],
            Intent.GENERATE_QUIZ: [
                r'\bquiz\b',
                r'\btest me\b',
                r'\bpractice\b',
                r'\bexercise\b',
                r'\bquestion\b',
                r'\bcheck my understanding\b',
                r'\bgenerate.*quiz\b',
                r'\bcreate.*test\b',
            ],
            Intent.ASSESS_ANSWERS: [
                r'\bgrade\b',
                r'\bcheck.*answer\b',
                r'\bmark.*answer\b',
                r'\bscore\b',
                r'\brate my answer\b',
                r'\bis this correct\b',
                r'\bsubmit.*answer\b',
                r'\bevaluate\b',
            ],
            Intent.RECOMMEND_NEXT: [
                r'\bwhat.*next\b',
                r'\brecommend\b',
                r'\bsuggest\b',
                r'\bwhat should i learn\b',
                r'\bwhere.*go from here\b',
                r'\bnext step\b',
                r'\bwhat.*do next\b',
            ],
            Intent.SUMMARIZE_LESSON: [
                r'\bsummarize\b',
                r'\bsummary\b',
                r'\bkey points\b',
                r'\bmain ideas\b',
                r'\boverview\b',
                r'\brecap\b',
                r'\bbriefly\b',
            ],
            Intent.ANSWER_QUESTION: [
                r'\bwhy\b',
                r'\bhow\b',
                r'\bwhen\b',
                r'\bwhere\b',
                r'\bwho\b',
                r'\bcan you\b',
                r'\?',  # Contains question mark
            ],
        }

        # Compile regex patterns for efficiency
        self.compiled_patterns: Dict[Intent, List[re.Pattern]] = {
            intent: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for intent, patterns in self.intent_patterns.items()
        }

    def classify(self, message: str) -> Intent:
        """
        Classify user message intent

        Args:
            message: User's natural language message

        Returns:
            Detected intent
        """
        message = message.lower().strip()

        # Score each intent based on pattern matches
        intent_scores: Dict[Intent, int] = {intent: 0 for intent in Intent}

        for intent, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(message):
                    intent_scores[intent] += 1

        # Get intent with highest score
        max_score = max(intent_scores.values())

        if max_score == 0:
            return Intent.UNKNOWN

        # Return intent with highest score
        # If tie, prioritize based on specificity
        priority_order = [
            Intent.GENERATE_QUIZ,
            Intent.ASSESS_ANSWERS,
            Intent.SIMPLIFY_CONTENT,
            Intent.SUMMARIZE_LESSON,
            Intent.EXPLAIN_LESSON,
            Intent.RECOMMEND_NEXT,
            Intent.ANSWER_QUESTION,
        ]

        for intent in priority_order:
            if intent_scores[intent] == max_score:
                return intent

        return Intent.UNKNOWN

    def classify_with_confidence(self, message: str) -> Tuple[Intent, float]:
        """
        Classify with confidence score

        Args:
            message: User's natural language message

        Returns:
            Tuple of (intent, confidence_score)
        """
        message = message.lower().strip()

        intent_scores: Dict[Intent, int] = {intent: 0 for intent in Intent}
        total_patterns = 0

        for intent, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                total_patterns += 1
                if pattern.search(message):
                    intent_scores[intent] += 1

        max_score = max(intent_scores.values())

        if max_score == 0:
            return Intent.UNKNOWN, 0.0

        # Calculate confidence based on match strength
        confidence = min(max_score / 3.0, 1.0)  # 3+ matches = 100% confidence

        # Get best intent
        priority_order = [
            Intent.GENERATE_QUIZ,
            Intent.ASSESS_ANSWERS,
            Intent.SIMPLIFY_CONTENT,
            Intent.SUMMARIZE_LESSON,
            Intent.EXPLAIN_LESSON,
            Intent.RECOMMEND_NEXT,
            Intent.ANSWER_QUESTION,
        ]

        for intent in priority_order:
            if intent_scores[intent] == max_score:
                return intent, confidence

        return Intent.UNKNOWN, 0.0

    def get_all_scores(self, message: str) -> Dict[Intent, int]:
        """
        Get scores for all intents (useful for debugging)

        Args:
            message: User's natural language message

        Returns:
            Dictionary of intent scores
        """
        message = message.lower().strip()
        intent_scores: Dict[Intent, int] = {intent: 0 for intent in Intent}

        for intent, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(message):
                    intent_scores[intent] += 1

        return intent_scores
