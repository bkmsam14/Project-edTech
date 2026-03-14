# AI Educational Platform - Orchestrator Agent

## Project Overview

This is the **Orchestrator Agent** component for an AI-powered educational platform designed to provide:
1. **Adaptive Learning & Personalization** - Personalized learning support based on student performance
2. **Inclusive Learning for Disabilities** - Specialized support for students with dyslexia

## Architecture

The Orchestrator Agent serves as the **traffic controller** that:
- Detects user intent from natural language requests
- Routes requests through appropriate learning workflows
- Coordinates multiple specialized agents
- Ensures accessibility adaptations
- Validates safety and grounding guardrails

## Directory Structure

```
src/orchestrator/
├── __init__.py                  # Package initialization
├── intent_classifier.py         # Detects user intent from messages
├── workflow_builder.py          # Builds execution workflows for each intent
├── orchestrator.py              # Main orchestrator controller
├── schemas.py                   # Data models (request, response, context)
├── example_usage.py             # Complete working examples
├── README.md                    # Comprehensive documentation
├── pytest.ini                   # Pytest configuration
└── tests/                       # Test suite
    ├── __init__.py
    ├── test_intent_classifier.py
    ├── test_workflow_builder.py
    └── test_orchestrator.py
```

## Core Components

### 1. Intent Classifier
**File:** `intent_classifier.py`

Classifies user requests into learning intents:
- `explain_lesson` - Request lesson explanation
- `simplify_content` - Request simplified content
- `answer_question` - Ask questions
- `generate_quiz` - Request quiz
- `assess_quiz` - Submit quiz answers
- `recommend_next` - Request recommendations

**Usage:**
```python
from intent_classifier import IntentClassifier

classifier = IntentClassifier()
intent, confidence = classifier.classify("Explain photosynthesis")
# Returns: (Intent.EXPLAIN_LESSON, 0.67)
```

### 2. Workflow Builder
**File:** `workflow_builder.py`

Defines workflow steps for each intent:
- `load_profile` - Load user profile
- `retrieve_lesson` - Retrieve lesson content (RAG)
- `adapt_accessibility` - Apply dyslexia adaptations
- `tutor_explanation` - Generate explanation
- `generate_quiz` - Create quiz
- `assess_quiz` - Evaluate answers
- `recommend` - Generate recommendations
- `validate_guardrails` - Validate safety

**Example Workflow (Explain Lesson):**
```
load_profile → retrieve_lesson → adapt_accessibility → tutor_explanation → validate_guardrails
```

### 3. Main Orchestrator
**File:** `orchestrator.py`

Executes workflows by:
1. Classifying intent
2. Building workflow
3. Executing steps sequentially
4. Sharing context across steps
5. Handling errors gracefully
6. Returning structured response

**Usage:**
```python
from orchestrator import Orchestrator
from schemas import OrchestratorRequest

orchestrator = Orchestrator()

# Register step handlers
orchestrator.register_step_handler(WorkflowStep.LOAD_PROFILE, my_handler)

# Process request
request = OrchestratorRequest(
    user_id="student_123",
    message="Explain algebra",
    lesson_id="math_101"
)

response = await orchestrator.process_request(request)
```

## Data Flow

```
User Request
    ↓
│ Intent Classification │
    ↓
│ Workflow Building │
    ↓
┌─────────────────────────────────┐
│ Workflow Execution:             │
│                                 │
│ 1. Load Profile                 │  ← Profile DB
│    ├─ Support mode (dyslexia)   │
│    ├─ Learning preferences      │
│    └─ Mastery levels            │
│                                 │
│ 2. Retrieve Lesson              │  ← Vector Store (RAG)
│    ├─ Search lesson content     │
│    ├─ Get relevant chunks       │
│    └─ Rank by relevance         │
│                                 │
│ 3. Adapt Accessibility          │  ← Accessibility Rules
│    ├─ Dyslexia-friendly font    │
│    ├─ Simplified language       │
│    ├─ Short sentences           │
│    └─ Visual spacing            │
│                                 │
│ 4. Tutor Explanation            │  ← Local LLM (≤5B params)
│    ├─ Generate explanation      │
│    ├─ Ground in lesson content  │
│    └─ Adapt to learning level   │
│                                 │
│ 5. Validate Guardrails          │  ← Validation Rules
│    ├─ Check lesson grounding    │
│    ├─ No diagnosis claims       │
│    ├─ Appropriate language      │
│    └─ Confidence score          │
└─────────────────────────────────┘
    ↓
Response to User
```

## Request/Response Format

### Request
```python
OrchestratorRequest(
    user_id="student_123",           # Required
    message="Explain photosynthesis", # Required
    lesson_id="biology_101",         # Optional
    session_id="session_xyz",        # Optional
    quiz_answers={...},              # Optional (for quiz assessment)
    metadata={...}                   # Optional
)
```

### Response
```python
OrchestratorResponse(
    success=True,
    intent=Intent.EXPLAIN_LESSON,
    message="Here's an explanation...",
    data={
        "explanation": "...",
        "accessibility": {...},
        "confidence": 0.92
    },
    workflow_steps_executed=[
        "load_profile",
        "retrieve_lesson",
        "adapt_accessibility",
        "tutor_explanation",
        "validate_guardrails"
    ],
    context=<WorkflowContext>
)
```

## Dyslexia Support

The orchestrator ensures accessibility for dyslexic students:

### Adaptations Applied
- **Font**: OpenDyslexic or similar dyslexia-friendly fonts
- **Font Size**: Larger (18-20pt)
- **Line Spacing**: Wider (1.5-2.0)
- **Text Chunking**: Short sentences, frequent paragraphs
- **Color Scheme**: Cream/off-white background
- **Language**: Simplified vocabulary, clear explanations
- **Structure**: Bullet points, numbered lists, visual hierarchy

### Example

**Original:**
```
Photosynthesis is the biochemical process by which plants,
algae, and some bacteria convert light energy into chemical
energy stored in glucose molecules, using carbon dioxide
and water as reactants.
```

**Dyslexia-Adapted:**
```
Photosynthesis is how plants make food.

Plants use:
• Sunlight (for energy)
• Water (from soil)
• Air (carbon dioxide)

They make:
• Sugar (food for the plant)
• Oxygen (we breathe this!)

Think of plants like little factories
that turn sunlight into food.
```

## Guardrails

All responses pass through validation:

### Validation Checks
1. **Grounding**: Only use retrieved lesson content
2. **No Diagnosis**: Never diagnose learning disabilities
3. **Scope**: Only answer lesson-related questions
4. **Language**: Age-appropriate, supportive tone
5. **Confidence**: Flag low-confidence responses

### Example
```python
{
    'grounded_in_lesson': True,
    'no_diagnosis_claims': True,
    'within_scope': True,
    'appropriate_language': True,
    'confidence_score': 0.92,
    'passed': True
}
```

## Integration Examples

### FastAPI Backend
```python
from fastapi import FastAPI
from orchestrator import Orchestrator
from schemas import OrchestratorRequest

app = FastAPI()
orchestrator = Orchestrator()

# Register handlers...

@app.post("/api/chat")
async def chat(user_id: str, message: str, lesson_id: str = None):
    request = OrchestratorRequest(
        user_id=user_id,
        message=message,
        lesson_id=lesson_id
    )

    response = await orchestrator.process_request(request)

    return {
        "success": response.success,
        "intent": response.intent.value,
        "message": response.message,
        "data": response.data
    }
```

### With Database & Vector Store
```python
# Step handlers that connect to real services

def load_profile_handler(context):
    # Connect to Profile DB
    profile = database.get_user_profile(context.request.user_id)
    context.user_profile = profile
    return profile

def retrieve_lesson_handler(context):
    # Connect to Vector Store (Chroma, Pinecone, etc.)
    chunks = vector_store.similarity_search(
        query=context.request.message,
        lesson_id=context.request.lesson_id,
        k=5
    )
    context.retrieved_chunks = chunks
    return {"chunks": chunks}

def tutor_explanation_handler(context):
    # Use local LLM (Phi-3, Gemma, Qwen)
    explanation = local_llm.generate(
        prompt=f"Explain: {context.request.message}",
        context=context.retrieved_chunks,
        max_tokens=200
    )
    return {"explanation": explanation}
```

## Running Examples

### Basic Example
```bash
cd src
python orchestrator/example_usage.py
```

**Output:**
```
============================================================
EXAMPLE 1: Explain Lesson Request
============================================================

User message: 'Can you explain what algebra is?'

Workflow execution:
  > Loading profile for user: student_123
  > Retrieving lesson: algebra_101
  > Adapting for support mode: dyslexia
  > Generating explanation for: Can you explain what algebra is?...
  > Validating output guardrails

[OK] Response:
  Success: True
  Intent: explain_lesson
  Message: Here's an explanation of the lesson content.
  Steps executed: load_profile, retrieve_lesson, adapt_accessibility,
                  tutor_explanation, validate_guardrails
```

### Running Tests
```bash
cd src/orchestrator
pytest tests/ -v
```

## Development Status

### ✅ Completed (MVP)
- [x] Intent classification (keyword-based)
- [x] Workflow building for all intents
- [x] Main orchestrator with step execution
- [x] Context sharing across steps
- [x] Error handling and recovery
- [x] Comprehensive data schemas
- [x] Working examples with mock handlers
- [x] Full test suite (90+ tests)
- [x] Comprehensive documentation

### 🚧 Next Steps (Integration)
- [ ] Implement actual step handlers (replace mocks)
- [ ] Connect to Profile Database
- [ ] Connect to Vector Store (RAG)
- [ ] Integrate local LLM (Phi-3/Gemma)
- [ ] Implement accessibility transformations
- [ ] Add guardrails validation logic
- [ ] Create FastAPI endpoints
- [ ] Add authentication/authorization
- [ ] Implement session management
- [ ] Add logging and monitoring

### 🔮 Future Enhancements
- [ ] Replace keyword classifier with ML model
- [ ] Add conversation history/memory
- [ ] Parallel step execution (where possible)
- [ ] Caching for frequent requests
- [ ] A/B testing framework
- [ ] Real-time analytics
- [ ] Multi-language support
- [ ] Voice interface support

## Technical Specifications

### Requirements
- Python 3.7+
- No external dependencies for orchestrator core
- Async/await support
- Type hints throughout

### Performance
- Synchronous step execution (predictable, debuggable)
- In-memory context (MVP - move to Redis for scale)
- Fail-fast on critical errors
- Comprehensive logging

### Code Quality
- Type hints on all functions
- Comprehensive docstrings
- 90+ unit tests
- Clean separation of concerns
- Modular, extensible design

## Contributing

### Adding New Intent
1. Add intent to `Intent` enum in `schemas.py`
2. Add keywords to `IntentClassifier` in `intent_classifier.py`
3. Define workflow in `WorkflowBuilder` in `workflow_builder.py`
4. Add tests

### Adding New Workflow Step
1. Add step to `WorkflowStep` enum in `schemas.py`
2. Create step handler function
3. Register handler in orchestrator
4. Add to appropriate workflows
5. Add tests

### Best Practices
- Keep step handlers focused and single-purpose
- Update context for data sharing across steps
- Log important events and errors
- Write tests for new functionality
- Update documentation

## Support

For questions or issues:
- Review the comprehensive README in `src/orchestrator/README.md`
- Check example usage in `src/orchestrator/example_usage.py`
- Run tests to verify setup: `pytest tests/ -v`
- Review test cases for usage patterns

## License

MIT License

---

## Quick Start Checklist

- [x] ✅ Install dependencies: None needed for core orchestrator
- [x] ✅ Review architecture documentation
- [x] ✅ Run example: `python src/orchestrator/example_usage.py`
- [ ] 🚧 Implement step handlers for your services
- [ ] 🚧 Connect to Profile Database
- [ ] 🚧 Connect to Vector Store
- [ ] 🚧 Integrate local LLM
- [ ] 🚧 Create FastAPI endpoints
- [ ] 🚧 Add authentication
- [ ] 🚧 Deploy and test

**The orchestrator core is complete and ready for integration!** 🎉
