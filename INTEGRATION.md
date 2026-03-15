# Integration Guide for Teammates

## Quick Start

### Installation
```bash
# No external dependencies needed - uses only Python standard library
python --version  # Requires Python 3.10+
```

### Run Tests
```bash
cd Project-edTech
python -m unittest tests.test_agents
```

### Run Demo
```bash
cd Project-edTech
python demo.py
```

### Start HTTP API
```bash
cd Project-edTech
python -m edtech_agents.http_api
# Server runs on http://127.0.0.1:8000
```

---

## API Endpoints

### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "ok",
  "service": "edtech-agents",
  "routes": ["/health", "/tutor", "/assessment"]
}
```

### Tutor Agent
```bash
POST /tutor
Content-Type: application/json

{
  "student_id": "stu-123",
  "question": "What is recursion?",
  "lesson_chunks": [
    "Recursion is when a function calls itself.",
    "Every recursive function needs a base case."
  ],
  "dyslexia_mode": true,
  "hints_used": 0
}
```

Response:
```json
{
  "student_id": "stu-123",
  "question": "What is recursion?",
  "hints": [
    {
      "level": 1,
      "support_level": "light",
      "text": "Focus on these key terms: **Recursion**, **function**, **calls**.",
      "tts_text": "Focus on these key terms: Recursion, function, calls."
    }
  ],
  "quiz": [
    {
      "type": "multiple_choice",
      "question": "____ is when a function calls itself.",
      "options": ["base", "calls", "function", "Recursion"],
      "correct_answer": "Recursion"
    }
  ],
  "dyslexia_mode": true
}
```

### Assessment Agent
```bash
POST /assessment
Content-Type: application/json

{
  "student_id": "stu-123",
  "question_id": "q-42",
  "student_answer": "base case",
  "correct_answer": "base case",
  "hints_used": 1,
  "topic": "recursion"
}
```

Response:
```json
{
  "student_id": "stu-123",
  "question_id": "q-42",
  "is_correct": true,
  "weakness_score": 0.1,
  "recommendation": {
    "next_action": "practice_same_topic",
    "topic": "recursion",
    "message": "The answer was correct, but the student still needs one more easy practice question."
  }
}
```

---

## Python Integration

### Direct Function Calls (Backend)

```python
from edtech_agents import tutor_agent, assessment_agent

# Get hints and quiz
result = tutor_agent(
    student_id="stu-123",
    question="How do I compare fractions?",
    lesson_chunks=["Fractions show parts of a whole.",
                   "Use common denominator to compare."],
    dyslexia_mode=True,
    hints_used=0
)

# Evaluate answer
assessment = assessment_agent(
    student_id="stu-123",
    question_id="q-1",
    student_answer="common denominator",
    correct_answer="common denominator",
    hints_used=1,
    topic="fractions"
)
```

### Service Handlers (Type-Safe)

```python
from edtech_agents import handle_tutor_request, handle_assessment_request

# Validates input and returns dict
tutor_response = handle_tutor_request({
    "student_id": "stu-123",
    "question": "What is a fraction?",
    "lesson_chunks": ["..."],
    "dyslexia_mode": True,
    "hints_used": 0
})

# Will raise AgentValidationError if invalid
assessment_response = handle_assessment_request({
    "student_id": "stu-123",
    "question_id": "q-1",
    "student_answer": "numerator",
    "correct_answer": "denominator",
    "hints_used": 2,
    "topic": "fractions"
})
```

---

## Data Flow

### Input (from your retrieval/orchestrator):
1. **Retrieval Agent** → provides `lesson_chunks` (from RAG/vector store)
2. **Orchestrator** → calls tutor agent with student question
3. **Frontend** → student submits answer
4. **Orchestrator** → calls assessment agent

### Output (to your frontend/database):
1. **Hints** → display step-by-step, support TTS with `tts_text`
2. **Quiz** → render multiple choice or short answer
3. **Assessment** → show correctness, update progress tracking
4. **Recommendation** → decide next action (next topic, retry, easier explanation)

---

## Adaptive Learning Flow

```
1. Student asks question
   ↓
2. Tutor Agent generates hints (level: light)
   ↓
3. Student requests more hints
   ↓
4. Tutor Agent provides more direct guidance (level: guided → direct)
   ↓
5. Student submits answer
   ↓
6. Assessment Agent evaluates:
   - Correct + no hints → next_topic
   - Correct + many hints → practice_same_topic
   - Wrong + low weakness → show_hint
   - Wrong + high weakness → easier_explanation
```

---

## Dyslexia-Friendly Features

The agents automatically:
- Break long sentences (max 14 words)
- Highlight key terms with `**bold**`
- Provide clean `tts_text` (no markdown) for text-to-speech
- Use simple, chunked explanations

Example:
```
Original: "Recursion is a programming technique where a function calls itself (also known as self-referential) to solve complex problems by breaking them down."

Dyslexia mode: "**Recursion** is a programming technique. A **function** calls itself. This solves **complex** problems."
```

---

## Student Topic Tracking

```python
from edtech_agents import get_student_topic_summary

summary = get_student_topic_summary("stu-123")
# {
#   "fractions": {
#     "attempts": 5,
#     "incorrect": 2,
#     "hints_used": 7,
#     "mastery_score": 0.65
#   },
#   "recursion": {
#     "attempts": 3,
#     "incorrect": 0,
#     "hints_used": 2,
#     "mastery_score": 0.92
#   }
# }
```

**Note**: This is in-memory only for hackathon. Your backend should persist to a database.

---

## Error Handling

```python
from edtech_agents import handle_tutor_request, AgentValidationError

try:
    result = handle_tutor_request({
        "student_id": "",  # Invalid: empty
        "question": "What is X?",
        "lesson_chunks": []  # Invalid: empty
    })
except AgentValidationError as e:
    print(f"Validation error: {e}")
    # Return 400 Bad Request to frontend
```

---

## Testing Your Integration

```bash
# Test health endpoint
curl http://127.0.0.1:8000/health

# Test tutor endpoint
curl -X POST http://127.0.0.1:8000/tutor \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test-123",
    "question": "What is recursion?",
    "lesson_chunks": ["Recursion is when a function calls itself."],
    "dyslexia_mode": true,
    "hints_used": 0
  }'

# Test assessment endpoint
curl -X POST http://127.0.0.1:8000/assessment \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test-123",
    "question_id": "q-1",
    "student_answer": "base case",
    "correct_answer": "base case",
    "hints_used": 1,
    "topic": "recursion"
  }'
```

---

## Frontend Integration Example

```javascript
// React/Vue/Angular example
async function getHints(studentId, question, lessonChunks, hintsUsed = 0) {
  const response = await fetch('http://127.0.0.1:8000/tutor', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      student_id: studentId,
      question: question,
      lesson_chunks: lessonChunks,
      dyslexia_mode: true,
      hints_used: hintsUsed
    })
  });

  const data = await response.json();

  // Display hints
  data.hints.forEach(hint => {
    console.log(`[${hint.support_level}] ${hint.text}`);
    // For TTS: speak(hint.tts_text)
  });

  // Display quiz
  data.quiz.forEach(q => {
    console.log(q.question);
    if (q.type === 'multiple_choice') {
      console.log('Options:', q.options);
    }
  });
}

async function submitAnswer(studentId, questionId, answer, correctAnswer, topic, hintsUsed) {
  const response = await fetch('http://127.0.0.1:8000/assessment', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      student_id: studentId,
      question_id: questionId,
      student_answer: answer,
      correct_answer: correctAnswer,
      hints_used: hintsUsed,
      topic: topic
    })
  });

  const result = await response.json();

  if (result.is_correct) {
    console.log('✓ Correct!');
  } else {
    console.log('✗ Incorrect');
  }

  console.log('Weakness score:', result.weakness_score);
  console.log('Next action:', result.recommendation.next_action);
  console.log('Message:', result.recommendation.message);
}
```

---

## FAQ

### Q: Do these agents use LLMs?
**A**: No, they're rule-based for hackathon simplicity. They use keyword extraction, sentence ranking, and fuzzy matching. This makes them:
- Fast and predictable
- No model download needed
- Fully deterministic
- Easy to debug

If you need LLM integration later, see `INTEGRATION_LLM.md` (to be created).

### Q: How accurate is the answer evaluation?
**A**: Uses `SequenceMatcher` for fuzzy matching (86% threshold). Handles:
- Case differences: "Base Case" = "base case" ✓
- Extra words: "the base case" ≈ "base case" ✓
- Typos: "bse case" ≈ "base case" (partial match)

### Q: How do I persist student data?
**A**: Currently in-memory. Your backend should:
1. Call assessment agent
2. Get the result
3. Save to your database (PostgreSQL, MongoDB, etc.)

### Q: Can I customize the hint generation?
**A**: Yes! Modify `edtech_agents/agents.py`:
- `generate_step_by_step_hints()` - adjust hint logic
- `simplify_for_dyslexia()` - customize text processing
- `_rank_sentences()` - change sentence prioritization

---

## Contact

For questions about the agents API, ask the team member responsible for this module.

**Files you need to integrate with:**
- `edtech_agents/service.py` - Main entry points
- `edtech_agents/http_api.py` - HTTP server
- `edtech_agents/models.py` - Request/response contracts
