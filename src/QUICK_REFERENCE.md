# Orchestrator Agent - Quick Reference

## 🚀 Quick Start

### 1. Run the Example
```bash
cd src
python orchestrator/example_usage.py
```

### 2. Basic Usage
```python
from orchestrator import Orchestrator
from schemas import OrchestratorRequest, WorkflowStep

# Create orchestrator
orchestrator = Orchestrator()

# Register handlers (replace with your actual implementations)
orchestrator.register_step_handler(WorkflowStep.LOAD_PROFILE, your_profile_handler)
orchestrator.register_step_handler(WorkflowStep.RETRIEVE_LESSON, your_rag_handler)
# ... register other handlers

# Process request
request = OrchestratorRequest(
    user_id="student_123",
    message="Explain photosynthesis",
    lesson_id="biology_101"
)

response = await orchestrator.process_request(request)
```

## 📋 Supported Intents

| Intent | Trigger Keywords | Example Message |
|--------|-----------------|-----------------|
| `explain_lesson` | explain, teach, what is, help me understand | "Explain photosynthesis" |
| `simplify_content` | simplify, simple, easier, basic | "Make this simpler" |
| `answer_question` | why, how, when, where, what causes | "Why do plants need water?" |
| `generate_quiz` | quiz, test, practice, check understanding | "Give me a quiz" |
| `assess_quiz` | submit, grade, check answers | "Here are my answers" |
| `recommend_next` | next, recommend, what should, suggest | "What should I learn next?" |
| `unknown` | (fallback) | Any unrecognized message |

## 🔄 Workflow Steps

| Step | Purpose | Updates Context With |
|------|---------|---------------------|
| `load_profile` | Load user profile from DB | `user_profile` |
| `retrieve_lesson` | Query vector store (RAG) | `lesson_content`, `retrieved_chunks` |
| `retrieve_history` | Get learning history | `learning_history` |
| `adapt_accessibility` | Apply dyslexia adaptations | `accessibility_adaptations` |
| `tutor_explanation` | Generate explanation (LLM) | Explanation in metadata |
| `generate_quiz` | Create quiz questions | Quiz in metadata |
| `assess_quiz` | Evaluate quiz answers | Assessment in metadata |
| `recommend` | Generate recommendations | Recommendations in metadata |
| `validate_guardrails` | Validate safety | Validation results |

## 🛠️ Step Handler Template

```python
def your_step_handler(context: WorkflowContext) -> dict:
    """
    Your step handler implementation

    Args:
        context: Shared workflow context

    Returns:
        dict: Results from this step
    """
    # 1. Read from context
    user_id = context.request.user_id
    message = context.request.message
    profile = context.user_profile  # If set by previous step

    # 2. Execute your logic
    result = your_service.do_something(user_id, message)

    # 3. Update context for next steps
    context.your_data = result

    # 4. Return data
    return result
```

## 🎯 Common Workflows

### Explain Lesson
```
load_profile → retrieve_lesson → adapt_accessibility → tutor_explanation → validate_guardrails
```

### Generate Quiz
```
load_profile → retrieve_lesson → generate_quiz → adapt_accessibility → validate_guardrails
```

### Assess Quiz
```
load_profile → assess_quiz → recommend → adapt_accessibility → validate_guardrails
```

### Recommend Next
```
load_profile → retrieve_history → recommend → validate_guardrails
```

## 📦 Request Schema

```python
OrchestratorRequest(
    user_id: str,              # REQUIRED - User identifier
    message: str,              # REQUIRED - User's message
    lesson_id: str = None,     # OPTIONAL - Current lesson
    session_id: str = None,    # OPTIONAL - Session ID
    quiz_answers: dict = None, # OPTIONAL - Quiz submission
    metadata: dict = None      # OPTIONAL - Extra data
)
```

## 📤 Response Schema

```python
OrchestratorResponse(
    success: bool,                      # Workflow success/failure
    intent: Intent,                     # Detected intent
    message: str,                       # Response message
    data: dict,                         # Response data
    workflow_steps_executed: List[str], # Steps that ran
    context: WorkflowContext            # Full context
)
```

## 🔍 Debugging

### Get Workflow Info (Without Executing)
```python
info = orchestrator.get_workflow_info("Explain photosynthesis")
# Returns: {
#     'intent': 'explain_lesson',
#     'confidence': 0.67,
#     'workflow_steps': ['load_profile', 'retrieve_lesson', ...]
# }
```

### Check Step Registration
```python
# Check if handler is registered
if WorkflowStep.LOAD_PROFILE in orchestrator.step_handlers:
    print("Profile handler registered")
```

### Access Response Context
```python
response = await orchestrator.process_request(request)

# Access shared context
user_profile = response.context.user_profile
lesson_chunks = response.context.retrieved_chunks
adaptations = response.context.accessibility_adaptations
```

## ⚠️ Error Handling

### Handle Failed Workflows
```python
response = await orchestrator.process_request(request)

if not response.success:
    print(f"Error: {response.message}")
    # Fallback logic here
else:
    # Process successful response
    data = response.data
```

### Try-Catch in Handlers
```python
def your_handler(context: WorkflowContext) -> dict:
    try:
        result = risky_operation()
        return result
    except SpecificError as e:
        # Log error
        logger.error(f"Step failed: {e}")
        # Re-raise to abort workflow
        raise
    except NonCriticalError as e:
        # Return fallback
        return {"fallback": True}
```

## 🎨 Dyslexia Adaptations

### Profile with Dyslexia Support
```python
user_profile = {
    'user_id': 'student_123',
    'support_mode': 'dyslexia',  # Enable dyslexia support
    'preferences': {
        'font_size': 'large',
        'line_spacing': 'wide',
        'use_tts': True
    }
}
```

### Accessibility Adaptations Applied
```python
adaptations = {
    'font': 'OpenDyslexic',
    'font_size': 18,
    'line_spacing': 2.0,
    'text_chunking': 'short_sentences',
    'color_scheme': 'cream_background',
    'simplified_language': True
}
```

## 🔒 Guardrails Validation

### Validation Template
```python
def validate_guardrails_handler(context: WorkflowContext) -> dict:
    validation = {
        'grounded_in_lesson': check_grounding(context),
        'no_diagnosis_claims': check_no_medical_claims(context),
        'within_scope': check_lesson_scope(context),
        'appropriate_language': check_language(context),
        'confidence_score': calculate_confidence(context),
        'passed': True
    }

    # Fail if any check fails
    if not all([
        validation['grounded_in_lesson'],
        validation['no_diagnosis_claims'],
        validation['within_scope']
    ]):
        validation['passed'] = False
        raise ValueError("Guardrail validation failed")

    return validation
```

## 🧪 Testing

### Run All Tests
```bash
cd src/orchestrator
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_orchestrator.py -v
```

### Run Single Test
```bash
pytest tests/test_orchestrator.py::TestOrchestratorInitialization::test_orchestrator_creation -v
```

## 📝 Adding New Intent

### 1. Add to Intent Enum
```python
# In schemas.py
class Intent(str, Enum):
    # ... existing intents
    NEW_INTENT = "new_intent"
```

### 2. Add Keywords
```python
# In intent_classifier.py
self.intent_keywords = {
    # ... existing intents
    Intent.NEW_INTENT: ["keyword1", "keyword2", "trigger"]
}
```

### 3. Define Workflow
```python
# In workflow_builder.py
def build_workflow(self, intent: Intent) -> List[WorkflowStep]:
    workflows = {
        # ... existing workflows
        Intent.NEW_INTENT: [
            WorkflowStep.LOAD_PROFILE,
            WorkflowStep.YOUR_CUSTOM_STEP,
            WorkflowStep.VALIDATE_GUARDRAILS
        ]
    }
```

### 4. Add Tests
```python
# In tests/test_intent_classifier.py
def test_new_intent(self, classifier):
    intent, conf = classifier.classify("trigger message")
    assert intent == Intent.NEW_INTENT
```

## 📝 Adding New Workflow Step

### 1. Add to WorkflowStep Enum
```python
# In schemas.py
class WorkflowStep(str, Enum):
    # ... existing steps
    YOUR_STEP = "your_step"
```

### 2. Implement Handler
```python
def your_step_handler(context: WorkflowContext) -> dict:
    # Your logic here
    result = do_something(context)
    context.your_data = result
    return result
```

### 3. Register Handler
```python
orchestrator.register_step_handler(
    WorkflowStep.YOUR_STEP,
    your_step_handler
)
```

### 4. Add to Workflows
```python
# In workflow_builder.py
Intent.SOME_INTENT: [
    WorkflowStep.LOAD_PROFILE,
    WorkflowStep.YOUR_STEP,  # Add your step
    WorkflowStep.VALIDATE_GUARDRAILS
]
```

## 🔗 Integration Examples

### FastAPI Endpoint
```python
from fastapi import FastAPI, HTTPException
from orchestrator import Orchestrator
from schemas import OrchestratorRequest

app = FastAPI()
orchestrator = Orchestrator()

@app.post("/api/chat")
async def chat(user_id: str, message: str, lesson_id: str = None):
    request = OrchestratorRequest(
        user_id=user_id,
        message=message,
        lesson_id=lesson_id
    )

    response = await orchestrator.process_request(request)

    if not response.success:
        raise HTTPException(status_code=500, detail=response.message)

    return {
        "intent": response.intent.value,
        "message": response.message,
        "data": response.data
    }
```

### With Database
```python
import asyncpg

async def load_profile_handler(context: WorkflowContext) -> dict:
    # Connect to PostgreSQL
    conn = await asyncpg.connect(DATABASE_URL)

    profile = await conn.fetchrow(
        "SELECT * FROM user_profiles WHERE user_id = $1",
        context.request.user_id
    )

    await conn.close()

    context.user_profile = dict(profile)
    return context.user_profile
```

### With Vector Store
```python
import chromadb

def retrieve_lesson_handler(context: WorkflowContext) -> dict:
    # Connect to ChromaDB
    client = chromadb.Client()
    collection = client.get_collection("lessons")

    # Query vector store
    results = collection.query(
        query_texts=[context.request.message],
        n_results=5,
        where={"lesson_id": context.request.lesson_id}
    )

    chunks = [
        {
            'chunk_id': id,
            'content': doc,
            'relevance_score': distance
        }
        for id, doc, distance in zip(
            results['ids'][0],
            results['documents'][0],
            results['distances'][0]
        )
    ]

    context.retrieved_chunks = chunks
    return {'chunks': chunks}
```

## 📚 Resources

- **Full Documentation**: `src/orchestrator/README.md`
- **Architecture Diagram**: `ARCHITECTURE.md`
- **Project Summary**: `PROJECT_SUMMARY.md`
- **Example Usage**: `src/orchestrator/example_usage.py`
- **Test Suite**: `src/orchestrator/tests/`

## 💡 Tips

1. **Start with examples**: Run `example_usage.py` first
2. **Use type hints**: They help catch errors early
3. **Log liberally**: Orchestrator logs all steps
4. **Test handlers**: Test each handler independently
5. **Check context**: Print context to debug workflows
6. **Handle errors**: Always handle potential failures
7. **Validate early**: Check inputs before processing
8. **Keep it simple**: Don't over-engineer handlers

## ⚡ Performance Tips

- Cache user profiles (Redis)
- Batch vector store queries
- Use async for I/O operations
- Implement request rate limiting
- Monitor slow steps
- Add timeouts to handlers
- Consider parallel execution for independent steps

## 🐛 Common Issues

### Intent Not Detected
**Solution**: Add more keywords to `intent_classifier.py`

### Workflow Fails
**Solution**: Check handler is registered and returns dict

### Context Empty
**Solution**: Ensure previous steps update context

### Validation Fails
**Solution**: Check guardrails logic and confidence thresholds

---

**Need help?** Check `example_usage.py` for working code! 🎉
