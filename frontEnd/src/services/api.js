/**
 * API service layer — single entry point for all backend calls
 */

const API_BASE = "/api/v1";

// ── token helpers ─────────────────────────────────────────────────────────────

export function getToken() {
  return localStorage.getItem("eduai_token") || null;
}

function setToken(token) {
  if (token) localStorage.setItem("eduai_token", token);
  else localStorage.removeItem("eduai_token");
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// ── base request ──────────────────────────────────────────────────────────────

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const config = {
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(options.headers || {}),
    },
    ...options,
  };
  delete config.headers; // rebuild cleanly
  config.headers = {
    "Content-Type": "application/json",
    ...authHeaders(),
    ...(options.headers || {}),
  };

  try {
    const res = await fetch(url, config);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `Request failed: ${res.status}`);
    return data;
  } catch (err) {
    console.error(`API ${options.method || "GET"} ${path} failed:`, err);
    throw err;
  }
}

// ── authentication ────────────────────────────────────────────────────────────

export async function signUp({ email, password, full_name }) {
  const data = await request("/auth/signup", {
    method: "POST",
    body: JSON.stringify({ email, password, full_name }),
  });
  // Persist token immediately
  setToken(data.access_token);
  if (data.user) localStorage.setItem("eduai_user", JSON.stringify(data.user));
  return data;
}

export async function signIn({ email, password }) {
  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  if (data.user) localStorage.setItem("eduai_user", JSON.stringify(data.user));
  return data;
}

export async function signOut() {
  try {
    await request("/auth/logout", { method: "POST" });
  } catch (_) { /* best-effort */ }
  setToken(null);
  localStorage.removeItem("eduai_user");
}

export function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem("eduai_user") || "null");
  } catch {
    return null;
  }
}

// --- Profile ---

export async function createProfile(profile) {
  return request("/profile", {
    method: "POST",
    body: JSON.stringify(profile),
  });
}

export async function getProfile(userId) {
  return request(`/profile/${userId}`);
}

// --- Lessons ---

export async function uploadLesson({ userId, title, content, subject, difficulty }) {
  return request("/lesson", {
    method: "POST",
    body: JSON.stringify({
      user_id: userId,
      title,
      content,
      subject: subject || "General",
      difficulty: difficulty || "intermediate",
    }),
  });
}

export async function listLessons() {
  return request("/lessons");
}

// --- Unified Learn Workflow ---

export async function learn({ userId, lessonId, documentId, courseId, question, intent, supportMode, preferredFormat }) {
  return request("/learn", {
    method: "POST",
    body: JSON.stringify({
      user_id: userId,
      lesson_id: lessonId || "",
      document_id: documentId || null,
      course_id: courseId || null,
      question,
      intent: intent || "explain",
      support_mode: supportMode || "phonological",
      preferred_format: preferredFormat || "simplified_text",
    }),
  });
}

// --- Individual endpoints ---

export async function explainLesson({ userId, message, lessonId }) {
  return request("/explain", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, message, lesson_id: lessonId || "" }),
  });
}

export async function simplifyContent({ userId, message, lessonId, adaptationType }) {
  return request("/simplify", {
    method: "POST",
    body: JSON.stringify({
      user_id: userId,
      message,
      lesson_id: lessonId || "",
      adaptation_type: adaptationType || "standard",
    }),
  });
}

export async function askQuestion({ userId, question, lessonId }) {
  return request("/qa", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, question, lesson_id: lessonId || "" }),
  });
}

export async function generateQuiz({ userId, lessonId, courseId, difficulty, numQuestions }) {
  return request("/quiz/generate", {
    method: "POST",
    body: JSON.stringify({
      user_id: userId,
      lesson_id: lessonId || "lesson_001",
      course_id: courseId || null,
      difficulty: difficulty || "medium",
      num_questions: numQuestions || 5,
    }),
  });
}

export async function submitAssessment({ userId, quizId, questions, answers }) {
  return request("/assessment/submit", {
    method: "POST",
    body: JSON.stringify({
      user_id: userId,
      quiz_id: quizId,
      questions,
      answers,
    }),
  });
}

export async function getRecommendations({ userId, depth }) {
  return request("/recommendations", {
    method: "POST",
    body: JSON.stringify({
      user_id: userId,
      depth: depth || 3,
    }),
  });
}

// --- Health ---

export async function healthCheck() {
  const res = await fetch("/health");
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || `Health check failed: ${res.status}`);
  return data;
}

// --- Moodle ---

export async function connectMoodle({ userId, sessionCookie }) {
  return request("/moodle/connect", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, session_cookie: sessionCookie }),
  });
}

export async function getMoodleCourses(userId) {
  return request(`/moodle/courses/${userId}`);
}

export async function selectMoodleCourse({ userId, courseId, courseName }) {
  return request("/moodle/select-course", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, course_id: courseId, course_name: courseName }),
  });
}

export async function getMoodleGrades(userId, courseId) {
  return request(`/moodle/grades/${userId}/${courseId}`);
}

export async function getMoodleStatus(userId) {
  return request(`/moodle/status/${userId}`);
}

// --- File Upload ---

export async function uploadLessonFile(formData) {
  const res = await fetch(`${API_BASE}/lesson/upload-file`, {
    method: "POST",
    body: formData,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || `Upload failed: ${res.status}`);
  return data;
}
