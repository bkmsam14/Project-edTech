# Orchestrator Agent

The **Orchestrator Agent** is the traffic controller for the AI educational platform. It routes user requests through the appropriate workflow pipeline by:

1. **Classifying user intent** from natural language
2. **Building a workflow** of required steps
3. **Executing the workflow** through registered agent handlers
4. **Validating outputs** through guardrails
5. **Returning structured responses**

## Architecture

```
User Request
    ↓
Intent Classifier → Detects what user wants
    ↓
Workflow Builder → Defines which agents to call
    ↓
Orchestrator → Executes workflow steps
    ↓
Response → Returns results to user
```

## Components

### 1. Intent Classifier (`intent_classifier.py`)

Detects user intent using keyword pattern matching.

**Supported Intents:**
- `EXPLAIN_LESSON` - Detailed explanations
- `SIMPLIFY_CONTENT` - Accessibility adaptations
- `GENERATE_QUIZ` - Quiz generation
- `ASSESS_ANSWERS` - Answer assessment
- `RECOMMEND_NEXT` - Next step recommendations
- `SUMMARIZE_LESSON` - Content summaries
- `ANSWER_QUESTION` - Q&A

**Usage:**
```python
classifier = IntentClassifier()
intent, confidence = classifier.classify_with_confidence(
    "Can you explain what photosynthesis is?"
)
# Returns: (Intent.EXPLAIN_LESSON, 0.87)
```

### 2. Workflow Builder (`workflow_builder.py`)

Defines execution workflows for each intent.

**Example Workflow for EXPLAIN_LESSON:**
1. Load user profile (dyslexia settings, preferences)
2. Retrieve lesson chunks (RAG)
3. Adapt for accessibility
4. Generate tutor explanation
5. Validate guardrails

**Usage:**
```python
builder = WorkflowBuilder()
workflow = builder.build_workflow(Intent.EXPLAIN_LESSON)
# Returns: [WorkflowStep.LOAD_PROFILE, WorkflowStep.RETRIEVE_LESSON, ...]
```

### 3. Orchestrator (`orchestrator.py`)

Main controller that executes workflows.

**Key Features:**
- **Step handlers** - Register agent implementations
- **Context management** - Maintains state across workflow
- **Error handling** - Graceful failures with fallbacks
- **Response building** - Structured output

**Usage:**
```python
orchestrator = Orchestrator()

# Register handlers
orchestrator.register_step_handler(
    WorkflowStep.LOAD_PROFILE,
    load_profile_handler
)

# Process request
request = OrchestratorRequest(
    user_id="student_123",
    message="Explain algebra",
    lesson_id="algebra_101"
)

response = await orchestrator.process_request(request)
```

### 4. Schemas (`schemas.py`)

Data models for type safety and validation.

**Key Schemas:**
- `OrchestratorRequest` - Input request
- `OrchestratorResponse` - Output response
- `WorkflowContext` - State during execution
- `Intent` - User intent enum
- `WorkflowStep` - Workflow step enum

## Workflow Definitions

### EXPLAIN_LESSON
```
Load Profile → Retrieve Lesson → Adapt Accessibility
→ Tutor Explanation → Validate Guardrails
```

**Use Case:** "Can you explain what mitosis is?"

### SIMPLIFY_CONTENT
```
Load Profile → Retrieve Lesson → Adapt Accessibility
→ Validate Guardrails
```

**Use Case:** "Make this simpler for me"

### GENERATE_QUIZ
```
Load Profile → Retrieve Lesson → Generate Quiz
→ Adapt Accessibility → Validate Guardrails
```

**Use Case:** "Give me a quiz on this topic"

### ASSESS_ANSWERS
```
Load Profile → Retrieve Lesson → Assess Quiz
→ Recommend → Validate Guardrails
```

**Use Case:** "Grade my answers"

### RECOMMEND_NEXT
```
Load Profile → Retrieve History → Recommend
→ Validate Guardrails
```

**Use Case:** "What should I learn next?"

## Integration Points

The orchestrator coordinates these agents:

1. **Learner Profile Module** - `WorkflowStep.LOAD_PROFILE`
2. **Retrieval Agent (RAG)** - `WorkflowStep.RETRIEVE_LESSON`
3. **Accessibility Agent** - `WorkflowStep.ADAPT_ACCESSIBILITY`
4. **Tutor Agent** - `WorkflowStep.TUTOR_EXPLANATION`
5. **Quiz Agent** - `WorkflowStep.GENERATE_QUIZ`
6. **Assessment Agent** - `WorkflowStep.ASSESS_QUIZ`
7. **Recommendation Agent** - `WorkflowStep.RECOMMEND`
8. **Guardrails** - `WorkflowStep.VALIDATE_GUARDRAILS`

## Example: Processing a Request

```python
# 1. User asks question
request = OrchestratorRequest(
    user_id="student_456",
    message="Can you explain photosynthesis in simple terms?",
    lesson_id="biology_101"
)

# 2. Orchestrator processes
response = await orchestrator.process_request(request)

# 3. Workflow execution:
#    ✓ Detected intent: EXPLAIN_LESSON
#    ✓ Loading profile for user: student_456
#    ✓ Retrieved 5 relevant lesson chunks
#    ✓ Adapted for dyslexia support mode
#    ✓ Generated explanation using Tutor Agent
#    ✓ Validated output (grounded, no claims, safe)

# 4. Response returned
{
    "success": true,
    "intent": "explain_lesson",
    "data": {
        "explanation": {
            "content": "Photosynthesis is how plants make food...",
            "adapted_for": "dyslexia"
        }
    },
    "message": "Here's an explanation of the lesson content.",
    "workflow_steps_executed": [
        "load_profile",
        "retrieve_lesson",
        "adapt_accessibility",
        "tutor_explanation",
        "validate_guardrails"
    ]
}
```

## Running the Example

```bash
cd src/orchestrator
python example_usage.py
```

This demonstrates:
- Intent classification
- Workflow execution
- Mock agent handlers
- Response generation

## For MVP Implementation

The orchestrator is **ready for MVP**. Next steps:

1. **Implement actual agent handlers** (replace mocks)
2. **Connect to data stores** (Profile DB, Vector DB)
3. **Integrate LLM** (local model ≤5B params)
4. **Add FastAPI endpoints** to expose orchestrator
5. **Build frontend** to send requests

## Extending the Orchestrator

### Add New Intent

```python
# 1. Add to Intent enum (schemas.py)
class Intent(Enum):
    MY_NEW_INTENT = "my_new_intent"

# 2. Add patterns (intent_classifier.py)
Intent.MY_NEW_INTENT: [
    r'\bmy pattern\b',
    r'\banother pattern\b',
]

# 3. Define workflow (workflow_builder.py)
Intent.MY_NEW_INTENT: [
    WorkflowStep.LOAD_PROFILE,
    WorkflowStep.MY_CUSTOM_STEP,
]

# 4. Register handler
orchestrator.register_step_handler(
    WorkflowStep.MY_CUSTOM_STEP,
    my_handler_function
)
```

### Add New Workflow Step

```python
# 1. Add to WorkflowStep enum (schemas.py)
class WorkflowStep(Enum):
    MY_STEP = "my_step"

# 2. Define prerequisites (workflow_builder.py)
WorkflowStep.MY_STEP: ['user_profile', 'lesson_content']

# 3. Implement handler
def my_step_handler(context: WorkflowContext):
    # Access context
    profile = context.user_profile
    lesson = context.lesson_content

    # Do work
    result = process_data(profile, lesson)

    # Return result
    return result

# 4. Register
orchestrator.register_step_handler(WorkflowStep.MY_STEP, my_step_handler)
```

## Design Decisions

### Why Rule-Based Intent Classification?

For MVP, keyword matching is:
- **Fast** - No model inference needed
- **Transparent** - Easy to debug
- **Sufficient** - Handles common patterns well

Can upgrade to ML-based classification later if needed.

### Why Workflow-Based Architecture?

Benefits:
- **Modularity** - Each agent is independent
- **Testability** - Test agents in isolation
- **Flexibility** - Easy to reorder/add steps
- **Observability** - Track which steps executed

### Guardrails Validation

Always runs last to ensure:
- Response is grounded in lesson content
- No medical/diagnosis claims (important for dyslexia support)
- Appropriate language level
- Within scope of request

## Future Enhancements

1. **ML-based intent classification** - Fine-tuned model
2. **Dynamic workflow adaptation** - Adjust based on context
3. **Parallel step execution** - Speed up independent steps
4. **Caching** - Reuse results for similar requests
5. **A/B testing** - Compare workflow variants
6. **Analytics** - Track success rates per intent

## License

Part of AI Educational Platform - Dyslexia Support System
