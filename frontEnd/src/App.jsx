import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import CreateProfile from './pages/CreateProfile'
import LessonSelection from './pages/LessonSelection'
import Workspace from './pages/Workspace'
import Quiz from './pages/Quiz'
import QuizResults from './pages/QuizResults'
import Home from './pages/Home'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/home" element={<Home />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/create-profile" element={<CreateProfile />} />
        <Route path="/lessons" element={<LessonSelection />} />
        <Route path="/workspace" element={<Workspace />} />
        <Route path="/quiz" element={<Quiz />} />
        <Route path="/quiz-results" element={<QuizResults />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
