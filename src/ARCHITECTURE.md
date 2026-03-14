# Orchestrator Agent Architecture

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                            │
│  "Can you explain what photosynthesis is?"                      │
│  lesson_id: "biology_101"                                       │
│  user_id: "student_123"                                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INTENT CLASSIFIER                            │
│  Analyzes message using keyword matching                        │
│  ─────────────────────────────────────────                      │
│  Keywords detected: ["explain", "what is"]                      │
│  → Intent: EXPLAIN_LESSON (confidence: 0.67)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW BUILDER                             │
│  Builds execution plan based on intent                          │
│  ─────────────────────────────────────────                      │
│  Intent: EXPLAIN_LESSON                                         │
│  → Workflow: [                                                  │
│      load_profile,                                              │
│      retrieve_lesson,                                           │
│      adapt_accessibility,                                       │
│      tutor_explanation,                                         │
│      validate_guardrails                                        │
│    ]                                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR EXECUTION                         │
│  Executes workflow steps sequentially                           │
└─────────────────────────────────────────────────────────────────┘
         │
         ├──── STEP 1: LOAD PROFILE ──────────────────────┐
         │     • Fetches user profile from database       │
         │     • Gets support_mode: "dyslexia"            │
         │     • Loads learning preferences               │
         │     • Updates shared context                   │
         │                                                 ▼
         │                          ┌────────────────────────────┐
         │                          │      PROFILE DATABASE      │
         │                          │  ┌──────────────────────┐  │
         │                          │  │ user_id: student_123 │  │
         │                          │  │ support_mode: dyslex │  │
         │                          │  │ preferences: {...}   │  │
         │                          │  │ mastery_levels: {...}│  │
         │                          │  └──────────────────────┘  │
         │                          └────────────────────────────┘
         │
         ├──── STEP 2: RETRIEVE LESSON ───────────────────┐
         │     • Queries vector store (RAG)               │
         │     • Searches for "photosynthesis"            │
         │     • Gets top 5 relevant chunks               │
         │     • Updates context with chunks              │
         │                                                 ▼
         │                          ┌────────────────────────────┐
         │                          │     VECTOR STORE (RAG)     │
         │                          │  ┌──────────────────────┐  │
         │                          │  │ Chunk 1: [0.95]      │  │
         │                          │  │ "Photosynthesis is   │  │
         │                          │  │  the process..."     │  │
         │                          │  ├──────────────────────┤  │
         │                          │  │ Chunk 2: [0.87]      │  │
         │                          │  │ "Plants use light to"│  │
         │                          │  └──────────────────────┘  │
         │                          └────────────────────────────┘
         │
         ├──── STEP 3: ADAPT ACCESSIBILITY ───────────────┐
         │     • Applies dyslexia-friendly adaptations    │
         │     • Sets font: OpenDyslexic                  │
         │     • Increases line spacing to 2.0            │
         │     • Enables text chunking                    │
         │     • Updates context with adaptations         │
         │                                                 ▼
         │                          ┌────────────────────────────┐
         │                          │  ACCESSIBILITY SETTINGS    │
         │                          │  ┌──────────────────────┐  │
         │                          │  │ font: OpenDyslexic   │  │
         │                          │  │ font_size: 18pt      │  │
         │                          │  │ line_spacing: 2.0    │  │
         │                          │  │ simplified: true     │  │
         │                          │  └──────────────────────┘  │
         │                          └────────────────────────────┘
         │
         ├──── STEP 4: TUTOR EXPLANATION ─────────────────┐
         │     • Generates explanation using local LLM    │
         │     • Grounds response in retrieved chunks     │
         │     • Adapts to dyslexia-friendly format       │
         │     • Creates simple, clear explanation        │
         │                                                 ▼
         │                          ┌────────────────────────────┐
         │                          │   LOCAL LLM (≤5B params)   │
         │                          │  ┌──────────────────────┐  │
         │                          │  │ Model: Phi-3 Mini    │  │
         │                          │  │ Input: Retrieved     │  │
         │                          │  │        chunks +      │  │
         │                          │  │        question      │  │
         │                          │  │ Output: Simplified   │  │
         │                          │  │         explanation  │  │
         │                          │  └──────────────────────┘  │
         │                          └────────────────────────────┘
         │
         └──── STEP 5: VALIDATE GUARDRAILS ──────────────┐
               • Checks grounding in lesson content      │
               • Verifies no diagnosis claims            │
               • Confirms appropriate language           │
               • Calculates confidence score             │
               • Validates response safety               │
                                                          ▼
                                ┌────────────────────────────┐
                                │   GUARDRAILS VALIDATION    │
                                │  ┌──────────────────────┐  │
                                │  │ grounded: ✓          │  │
                                │  │ no_diagnosis: ✓      │  │
                                │  │ within_scope: ✓      │  │
                                │  │ confidence: 0.92     │  │
                                │  │ passed: TRUE         │  │
                                │  └──────────────────────┘  │
                                └────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR RESPONSE                      │
│  ─────────────────────────────────────────────────────────────  │
│  Success: true                                                  │
│  Intent: explain_lesson                                         │
│  Message: "Here's an explanation of photosynthesis..."          │
│  Data: {                                                        │
│    "explanation": "Photosynthesis is how plants make food...",  │
│    "accessibility": {                                           │
│      "font": "OpenDyslexic",                                    │
│      "font_size": 18,                                           │
│      "line_spacing": 2.0                                        │
│    },                                                           │
│    "confidence": 0.92                                           │
│  }                                                              │
│  Steps Executed: [load_profile, retrieve_lesson,               │
│                   adapt_accessibility, tutor_explanation,       │
│                   validate_guardrails]                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  Displays dyslexia-friendly explanation with:                   │
│  • Large, clear font                                            │
│  • Wide line spacing                                            │
│  • Simple language                                              │
│  • Short paragraphs                                             │
│  • Bullet points and visual hierarchy                           │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Examples by Intent

### 1. Explain Lesson
```
User: "Explain photosynthesis"
Flow: profile → retrieve → accessibility → explain → validate
Output: Simplified, grounded explanation
```

### 2. Generate Quiz
```
User: "Give me a quiz"
Flow: profile → retrieve → quiz → accessibility → validate
Output: Dyslexia-friendly quiz questions
```

### 3. Assess Quiz
```
User: "Here are my answers" + answers
Flow: profile → assess → recommend → accessibility → validate
Output: Feedback + weak topics + recommendations
```

### 4. Simplify Content
```
User: "Make this simpler"
Flow: profile → retrieve → accessibility → validate
Output: Enhanced simplification adaptations
```

### 5. Recommend Next
```
User: "What should I learn next?"
Flow: profile → history → recommend → validate
Output: Personalized learning recommendations
```

## Context Flow Across Steps

```
┌────────────────────────────────────────┐
│        WORKFLOW CONTEXT (Shared)       │
├────────────────────────────────────────┤
│  request: OrchestratorRequest          │
│    ├─ user_id                          │
│    ├─ message                          │
│    └─ lesson_id                        │
│                                        │
│  user_profile: dict                    │  ← Set by load_profile
│    ├─ support_mode: "dyslexia"        │
│    ├─ preferences: {...}               │
│    └─ mastery_levels: {...}            │
│                                        │
│  lesson_content: dict                  │  ← Set by retrieve_lesson
│    ├─ lesson_id                        │
│    ├─ title                            │
│    └─ chunks: [...]                    │
│                                        │
│  retrieved_chunks: List[dict]          │  ← Set by retrieve_lesson
│    └─ [{chunk_id, content, score}]    │
│                                        │
│  accessibility_adaptations: dict       │  ← Set by adapt_accessibility
│    ├─ font                             │
│    ├─ font_size                        │
│    ├─ line_spacing                     │
│    └─ simplified_language              │
│                                        │
│  metadata: dict                        │  ← Updated by all steps
│    └─ {step_results, timestamps, etc} │
└────────────────────────────────────────┘
     Each step reads from and writes to
     this shared context object
```

## Component Interaction

```
┌──────────────────────┐
│  IntentClassifier    │
│  ─────────────────   │
│  • Keyword matching  │
│  • Confidence calc   │
│  • Intent detection  │
└──────────┬───────────┘
           │
           │ Intent + Confidence
           │
           ▼
┌──────────────────────┐
│  WorkflowBuilder     │
│  ─────────────────   │
│  • Intent → Steps    │
│  • Step ordering     │
│  • Workflow config   │
└──────────┬───────────┘
           │
           │ Workflow Steps List
           │
           ▼
┌──────────────────────┐
│  Main Orchestrator   │
│  ─────────────────   │
│  • Step execution    │
│  • Context sharing   │
│  • Error handling    │
│  • Response building │
└──────────┬───────────┘
           │
           │ Calls registered handlers
           │
           ▼
┌────────────────────────────────────┐
│      Step Handlers (Agents)        │
│  ────────────────────────────────  │
│  • Profile Agent                   │
│  • Retrieval Agent (RAG)           │
│  • Accessibility Agent             │
│  • Tutor Agent (LLM)               │
│  • Quiz Agent                      │
│  • Assessment Agent                │
│  • Recommendation Agent            │
│  • Guardrails Validator            │
└────────────────────────────────────┘
```

## Error Handling Flow

```
Step Execution
      │
      ├─ Try Execute Handler
      │       │
      │       ├─ SUCCESS ──────────► Continue to next step
      │       │
      │       └─ ERROR
      │           │
      │           ├─ Log error details
      │           │
      │           ├─ Check if critical step
      │           │    │
      │           │    ├─ YES ──► Abort workflow
      │           │    │          Return error response
      │           │    │
      │           │    └─ NO ───► Continue with fallback
      │           │
      │           └─ Return graceful error response
      │
      └─ Missing Handler
           │
           └─ Log warning ──► Skip step or abort
```

## Key Features

✅ **Intent Detection** - Keyword-based classification with confidence scores
✅ **Workflow Routing** - Dynamic workflow building based on intent
✅ **Sequential Execution** - Predictable, debuggable step execution
✅ **Context Sharing** - Shared state across all workflow steps
✅ **Error Recovery** - Graceful handling of failures
✅ **Accessibility** - Built-in dyslexia support
✅ **Guardrails** - Safety and grounding validation
✅ **Extensible** - Easy to add new intents and steps
✅ **Testable** - Comprehensive test suite
✅ **Production-Ready** - Logging, error handling, type hints
