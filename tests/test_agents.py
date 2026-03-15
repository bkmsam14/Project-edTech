import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from edtech_agents import (
    AgentValidationError,
    AgentHTTPRequestHandler,
    AssessmentRequest,
    TutorRequest,
    assessment_agent,
    build_http_server,
    generate_quiz,
    get_student_topic_summary,
    handle_assessment_request,
    handle_tutor_request,
    reset_student_topic_history,
    tutor_agent,
)


LESSON_CHUNKS = [
    "Fractions show equal parts of a whole. The denominator tells how many equal parts exist. The numerator tells how many parts are selected.",
    "To compare fractions, use a common denominator or compare the size of each part first.",
]


class TutorAgentTests(unittest.TestCase):
    def setUp(self):
        reset_student_topic_history()

    def test_tutor_agent_returns_grounded_hints_and_quiz(self):
        result = tutor_agent(
            student_id="stu-1",
            question="How do I compare fractions?",
            lesson_chunks=LESSON_CHUNKS,
            dyslexia_mode=True,
        )

        self.assertGreaterEqual(len(result["hints"]), 2)
        self.assertLessEqual(len(result["quiz"]), 3)
        self.assertTrue(all("text" in hint for hint in result["hints"]))
        self.assertTrue(all(question["correct_answer"] for question in result["quiz"]))

    def test_more_hints_make_support_more_direct(self):
        result = tutor_agent(
            student_id="stu-1",
            question="What does the denominator mean?",
            lesson_chunks=LESSON_CHUNKS,
            dyslexia_mode=False,
            hints_used=2,
        )

        self.assertEqual(result["hints"][0]["support_level"], "direct")
        self.assertGreaterEqual(len(result["hints"]), 3)

    def test_generate_quiz_limits_question_count(self):
        quiz = generate_quiz(LESSON_CHUNKS, question="fractions", max_questions=2)

        self.assertEqual(len(quiz), 2)

    def test_handle_tutor_request_returns_contract_ready_dict(self):
        payload = handle_tutor_request(
            {
                "student_id": "stu-10",
                "question": "What does the denominator tell us?",
                "lesson_chunks": LESSON_CHUNKS,
                "dyslexia_mode": True,
                "hints_used": 1,
            }
        )

        self.assertEqual(payload["student_id"], "stu-10")
        self.assertIn("hints", payload)
        self.assertIn("quiz", payload)
        self.assertTrue(all("tts_text" in hint for hint in payload["hints"]))

    def test_tutor_request_validation_rejects_empty_chunks(self):
        with self.assertRaises(ValueError):
            TutorRequest(
                student_id="stu-11",
                question="What is a fraction?",
                lesson_chunks=[],
            )

        with self.assertRaises(AgentValidationError):
            handle_tutor_request(
                {
                    "student_id": "stu-11",
                    "question": "What is a fraction?",
                    "lesson_chunks": [],
                }
            )


class AssessmentAgentTests(unittest.TestCase):
    def setUp(self):
        reset_student_topic_history()

    def test_assessment_marks_exact_match_correct(self):
        result = assessment_agent(
            student_id="stu-2",
            question_id="q-1",
            student_answer="common denominator",
            correct_answer="common denominator",
            hints_used=0,
            topic="fractions",
        )

        self.assertTrue(result["is_correct"])
        self.assertLess(result["weakness_score"], 0.3)
        self.assertEqual(result["recommendation"]["next_action"], "next_topic")

    def test_assessment_raises_weakness_for_wrong_answer_and_hints(self):
        result = assessment_agent(
            student_id="stu-2",
            question_id="q-2",
            student_answer="add the top numbers only",
            correct_answer="common denominator",
            hints_used=3,
            topic="fractions",
        )

        self.assertFalse(result["is_correct"])
        self.assertGreaterEqual(result["weakness_score"], 0.7)
        self.assertEqual(result["recommendation"]["next_action"], "easier_explanation")

    def test_topic_summary_tracks_attempts(self):
        assessment_agent(
            student_id="stu-3",
            question_id="q-3",
            student_answer="numerator",
            correct_answer="denominator",
            hints_used=1,
            topic="fractions",
        )
        summary = get_student_topic_summary("stu-3")

        self.assertEqual(summary["fractions"]["attempts"], 1)
        self.assertEqual(summary["fractions"]["incorrect"], 1)

    def test_handle_assessment_request_supports_multiple_choice_style_answers(self):
        payload = handle_assessment_request(
            {
                "student_id": "stu-4",
                "question_id": "q-4",
                "student_answer": "Base Case",
                "correct_answer": "base case",
                "hints_used": 0,
                "topic": "recursion",
            }
        )

        self.assertTrue(payload["is_correct"])
        self.assertEqual(payload["recommendation"]["next_action"], "next_topic")

    def test_assessment_request_validation_rejects_missing_topic(self):
        with self.assertRaises(ValueError):
            AssessmentRequest(
                student_id="stu-5",
                question_id="q-5",
                student_answer="",
                correct_answer="base case",
                hints_used=0,
                topic="",
            )

        with self.assertRaises(AgentValidationError):
            handle_assessment_request(
                {
                    "student_id": "stu-5",
                    "question_id": "q-5",
                    "student_answer": "",
                    "correct_answer": "base case",
                    "hints_used": 0,
                    "topic": "",
                }
            )


class AgentHttpApiTests(unittest.TestCase):
    def setUp(self):
        reset_student_topic_history()
        self.server = build_http_server(host="127.0.0.1", port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address
        self.base_url = f"http://{host}:{port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_health_endpoint_returns_ok(self):
        with urlopen(f"{self.base_url}/health") as response:
            payload = json.loads(response.read().decode("utf-8"))

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["status"], "ok")
        self.assertIn("/tutor", payload["routes"])

    def test_tutor_endpoint_returns_agent_payload(self):
        request = Request(
            url=f"{self.base_url}/tutor",
            data=json.dumps(
                {
                    "student_id": "stu-12",
                    "question": "How do I compare fractions?",
                    "lesson_chunks": LESSON_CHUNKS,
                    "dyslexia_mode": True,
                    "hints_used": 1,
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urlopen(request) as response:
            payload = json.loads(response.read().decode("utf-8"))

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["student_id"], "stu-12")
        self.assertTrue(payload["hints"])
        self.assertTrue(payload["quiz"])

    def test_assessment_endpoint_returns_validation_error_for_bad_payload(self):
        request = Request(
            url=f"{self.base_url}/assessment",
            data=json.dumps(
                {
                    "student_id": "stu-13",
                    "question_id": "q-13",
                    "student_answer": "",
                    "correct_answer": "base case",
                    "hints_used": 0,
                    "topic": "",
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with self.assertRaises(HTTPError) as error_context:
            urlopen(request)

        error_response = error_context.exception
        self.assertEqual(error_response.code, 400)
        payload = json.loads(error_response.read().decode("utf-8"))
        error_response.close()
        self.assertIn("Invalid assessment request", payload["error"])


if __name__ == "__main__":
    unittest.main()
