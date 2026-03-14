# Project-edTech

This workspace currently contains the Tutor Agent and Assessment Agent implementation for the hackathon scope.

## What is implemented

- Tutor Agent: grounded step-by-step hints from lesson chunks, dyslexia-friendly formatting, and quiz generation
- Assessment Agent: answer evaluation, weakness scoring, topic tracking in memory, and next-step recommendations
- Integration layer: request validation plus dict-in/dict-out service functions for backend/orchestrator calls
- No retrieval, database, frontend, MCP, or orchestration code

## File layout

- `edtech_agents/agents.py`: core agent logic
- `edtech_agents/models.py`: typed request and response models
- `edtech_agents/service.py`: orchestrator-friendly handlers
- `edtech_agents/http_api.py`: tiny HTTP wrapper for teammate integration
- `edtech_agents/__init__.py`: package exports
- `tests/test_agents.py`: unit tests

## Tutor Agent

```python
from edtech_agents import tutor_agent

result = tutor_agent(
	student_id="stu-100",
	question="How do I compare fractions?",
	lesson_chunks=[
		"Fractions show equal parts of a whole. The denominator tells how many equal parts exist.",
		"To compare fractions, use a common denominator or compare the size of each part first.",
	],
	dyslexia_mode=True,
	hints_used=0,
)
```

Backend-facing entry point:

```python
from edtech_agents import handle_tutor_request

payload = handle_tutor_request(
	{
		"student_id": "stu-100",
		"question": "How do I compare fractions?",
		"lesson_chunks": [
			"Fractions show equal parts of a whole.",
			"To compare fractions, use a common denominator.",
		],
		"dyslexia_mode": True,
		"hints_used": 1,
	}
)
```

Returned shape:

```python
{
	"student_id": "stu-100",
	"question": "How do I compare fractions?",
	"hints": [
		{
			"level": 1,
			"support_level": "light",
			"text": "Focus on these key terms: **compare**, **fractions**, **common**.",
			"tts_text": "Focus on these key terms: compare, fractions, common.",
		}
	],
	"quiz": [
		{
			"type": "multiple_choice",
			"question": "To compare fractions, use a common ____ or compare the size of each part first.",
			"options": ["Fractions", "common", "denominator", "parts"],
			"correct_answer": "denominator",
		}
	],
	"dyslexia_mode": True,
}
```

## Assessment Agent

```python
from edtech_agents import assessment_agent

result = assessment_agent(
	student_id="stu-100",
	question_id="q-42",
	student_answer="common denominator",
	correct_answer="common denominator",
	hints_used=1,
	topic="fractions",
)
```

Backend-facing entry point:

```python
from edtech_agents import handle_assessment_request

payload = handle_assessment_request(
	{
		"student_id": "stu-100",
		"question_id": "q-42",
		"student_answer": "common denominator",
		"correct_answer": "common denominator",
		"hints_used": 1,
		"topic": "fractions",
	}
)
```

Returned shape:

```python
{
	"student_id": "stu-100",
	"question_id": "q-42",
	"is_correct": True,
	"weakness_score": 0.1,
	"recommendation": {
		"next_action": "next_topic",
		"topic": "fractions",
		"message": "Move to the next topic or a slightly harder question.",
	},
}
```

## Notes for teammates

- These agents are deterministic and grounded only in `lesson_chunks` or provided answers
- Topic tracking is in-memory only for hackathon use; your backend can persist results elsewhere
- `tts_text` is included so the frontend can send plain text to audio/TTS components
- `handle_tutor_request` and `handle_assessment_request` are the safest entry points if your backend sends JSON-like dict payloads

## HTTP API

Run the local API server:

```bash
python -m edtech_agents.http_api
```

Routes:

- `GET /health`
- `POST /tutor`
- `POST /assessment`

Example tutor request:

```bash
curl -X POST http://127.0.0.1:8000/tutor \
	-H "Content-Type: application/json" \
	-d '{
		"student_id": "stu-100",
		"question": "How do I compare fractions?",
		"lesson_chunks": [
			"Fractions show equal parts of a whole.",
			"To compare fractions, use a common denominator."
		],
		"dyslexia_mode": true,
		"hints_used": 1
	}'
```

Example assessment request:

```bash
curl -X POST http://127.0.0.1:8000/assessment \
	-H "Content-Type: application/json" \
	-d '{
		"student_id": "stu-100",
		"question_id": "q-42",
		"student_answer": "common denominator",
		"correct_answer": "common denominator",
		"hints_used": 1,
		"topic": "fractions"
	}'
```

## Run tests

```bash
python -m unittest tests.test_agents
```
