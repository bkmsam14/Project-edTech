# FastAPI Endpoints for EduAI

This folder contains FastAPI endpoints for the AI Educational Platform with Dyslexia Support.

## Structure

```
APIendpoints/
├── main.py              # FastAPI app setup and route registration
├── models.py            # Pydantic request/response schemas
├── requirements.txt     # Python dependencies
├── routes/              # Individual endpoint handlers
│   ├── explain.py      # Lesson explanation endpoint
│   ├── simplify.py     # Content simplification endpoint
│   ├── quiz.py         # Quiz generation endpoint
│   ├── assessment.py   # Answer assessment endpoint
│   ├── recommendations.py  # Learning recommendations endpoint
│   └── qa.py           # Q&A endpoint
└── README.md           # This file
```

## Setup

1. Install dependencies:
```bash
cd APIendpoints
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/health` - Check if API is running
- **GET** `/` - API information

### Learning Endpoints

#### 1. Explain Lesson
- **POST** `/api/v1/explain`
- **Purpose**: Get detailed explanation of a lesson
- **Request**:
```json
{
    "user_id": "student_123",
    "lesson_id": "biology_101",
    "message": "Can you explain photosynthesis?",
    "context": "Optional context"
}
```

#### 2. Simplify Content
- **POST** `/api/v1/simplify`
- **Purpose**: Simplify content for accessibility needs
- **Request**:
```json
{
    "user_id": "student_456",
    "lesson_id": "biology_101",
    "message": "The content to simplify...",
    "adaptation_type": "dyslexia"
}
```

#### 3. Generate Quiz
- **POST** `/api/v1/quiz/generate`
- **Purpose**: Create quiz questions for a lesson
- **Request**:
```json
{
    "user_id": "student_123",
    "lesson_id": "algebra_101",
    "num_questions": 5,
    "difficulty": "medium"
}
```

#### 4. Submit Assessment
- **POST** `/api/v1/assessment/submit`
- **Purpose**: Grade quiz answers and provide feedback
- **Request**:
```json
{
    "user_id": "student_123",
    "lesson_id": "algebra_101",
    "answers": {
        "q1": "answer1",
        "q2": "answer2"
    },
    "quiz_id": "quiz_001"
}
```

#### 5. Get Recommendations
- **POST** `/api/v1/recommendations`
- **Purpose**: Get personalized learning recommendations
- **Request**:
```json
{
    "user_id": "student_123",
    "current_lesson_id": "algebra_101",
    "depth": 3
}
```

#### 6. Q&A
- **POST** `/api/v1/qa`
- **Purpose**: Answer a user's question about a lesson
- **Request**:
```json
{
    "user_id": "student_123",
    "question": "What is photosynthesis?",
    "lesson_id": "biology_101"
}
```

## Response Format

All responses follow a consistent structure:

```json
{
    "success": true,
    "intent": "explain_lesson",
    "message": "Description of what was done",
    "workflow_steps_executed": [
        "load_profile",
        "retrieve_lesson",
        "adapt_accessibility",
        "tutor_explanation",
        "validate_guardrails"
    ],
    "user_id": "student_123",
    "timestamp": "2024-03-14T10:30:00",
    "data": {
        "explanation": {
            "content": "...",
            "adapted_for": "dyslexia"
        }
    }
}
```

## Interactive Documentation

Once the server is running, visit:
- **Swagger UI** (interactive docs): `http://localhost:8000/docs`
- **ReDoc** (alternative docs): `http://localhost:8000/redoc`

## Integration with Orchestrator

These endpoints integrate with the orchestrator in `Project-edTech/src/orchestrator/`:
- Intent classification
- Workflow building
- Step execution
- Response validation

## Next Steps

- Connect endpoints to actual agent handlers (replace mock implementations)
- Integrate with data stores (user profiles, vector DB for RAG)
- Add authentication/authorization
- Implement caching for performance
- Add rate limiting
- Deploy to production

## Development

To run in development mode with hot reload:
```bash
uvicorn main:app --reload
```

To run with specific host/port:
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

## Testing

Test endpoints with curl:
```bash
curl -X POST "http://localhost:8000/api/v1/explain" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "student_123",
    "lesson_id": "biology_101",
    "message": "Explain photosynthesis",
    "context": null
  }'
```

Or use the Swagger UI at `/docs` for interactive testing.
