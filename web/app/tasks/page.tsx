// web/app/tasks/page.tsx
"use client";

import { useState, useEffect } from "react";

interface Task {
  id: number;
  image_path: string;
  answer_type: string;
  solution_image_path?: string;
  correct_option?: string;
}

interface CheckResult {
  correct: boolean;
  correct_answer?: string;
  solution_image_path?: string;
}

export default function TasksPage() {
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userAnswer, setUserAnswer] = useState("");
  const [checkResult, setCheckResult] = useState<CheckResult | null>(null);
  const [showSolution, setShowSolution] = useState(false);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetchRandomTask();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchRandomTask = async () => {
    setLoading(true);
    setError(null);
    setCheckResult(null);
    setShowSolution(false);
    setUserAnswer("");
    try {
      const url = `${apiUrl}/api/task/random`;
      const res = await fetch(url);
      if (!res.ok) {
        if (res.status === 404) {
          throw new Error("Есептер табылмады. Әзірше есептер қосылмаған.");
        }
        throw new Error(`Сервер қатесі: ${res.status}`);
      }
      const data = await res.json();
      setTask(data);
    } catch (err) {
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError(`API серверіне қосылу мүмкін емес.\n\nBot серверін іске қосыңыз:\ncd bot && python main.py\n\nСервер: ${apiUrl}`);
      } else {
        setError(err instanceof Error ? err.message : "Қате болды");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async (answer: string) => {
    if (!task) return;
    
    try {
      const res = await fetch(`${apiUrl}/api/task/check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          task_id: task.id,
          answer: answer,
          user_id: 0,
          email: ""
        })
      });
      
      if (!res.ok) throw new Error("Жауапты тексеру мүмкін болмады");
      
      const result: CheckResult = await res.json();
      setCheckResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Қате болды");
    }
  };

  const handleQuizAnswer = (option: string) => {
    setUserAnswer(option);
    handleSubmitAnswer(option);
  };

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (userAnswer.trim()) {
      handleSubmitAnswer(userAnswer);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Есеп жүктелуде...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 px-4">
        <div className="text-center max-w-2xl p-8 bg-white rounded-2xl shadow-xl">
          <h2 className="text-2xl font-bold text-red-600 mb-4">⚠️ Қате</h2>
          <pre className="text-left text-gray-700 mb-6 whitespace-pre-wrap bg-gray-50 p-4 rounded-lg border border-gray-200 text-sm">{error}</pre>
          <div className="space-y-3">
            <button
              onClick={fetchRandomTask}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition"
            >
              🔄 Қайталап көру
            </button>
            <a
              href="/"
              className="block text-blue-600 hover:text-blue-800 font-semibold underline"
            >
              ← Басты бетке қайту
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="text-center max-w-md p-8 bg-white rounded-2xl shadow-xl">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Есептер жоқ</h2>
          <p className="text-gray-600">Әзірше шешуге есептер қосылмаған</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Есеп #{task.id}</h1>
            <p className="text-gray-600">
              Түрі: {task.answer_type === "quiz" ? "Тест (A/B/C/D)" : "Қолмен енгізу"}
            </p>
          </div>

          <div className="mb-8">
            <img
              src={`${apiUrl}/${task.image_path}`}
              alt={`Есеп ${task.id}`}
              className="w-full rounded-lg shadow-md"
            />
          </div>

          {!checkResult && (
            <div className="mb-6">
              {task.answer_type === "quiz" ? (
                <div className="grid grid-cols-2 gap-4">
                  {["A", "B", "C", "D"].map((option) => (
                    <button
                      key={option}
                      onClick={() => handleQuizAnswer(option)}
                      className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white font-bold py-4 px-6 rounded-lg transition shadow-lg transform hover:scale-105"
                    >
                      {option}
                    </button>
                  ))}
                </div>
              ) : (
                <form onSubmit={handleTextSubmit} className="space-y-4">
                  <input
                    type="text"
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                    placeholder="Жауабыңызды енгізіңіз"
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none text-lg"
                  />
                  <button
                    type="submit"
                    className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-3 px-6 rounded-lg transition shadow-lg"
                  >
                    Жауапты тексеру
                  </button>
                </form>
              )}
            </div>
          )}

          {checkResult && (
            <div className={`mb-6 p-6 rounded-lg ${checkResult.correct ? 'bg-green-100 border-2 border-green-500' : 'bg-red-100 border-2 border-red-500'}`}>
              <p className="text-xl font-bold mb-2">
                {checkResult.correct ? '✅ Дұрыс!' : '❌ Қате'}
              </p>
              {!checkResult.correct && checkResult.correct_answer && (
                <p className="text-lg">Дұрыс жауап: <span className="font-bold">{checkResult.correct_answer}</span></p>
              )}
              {checkResult.correct && <p className="text-green-700">+1 ұпай</p>}
              
              <div className="mt-4 space-x-4">
                {checkResult.solution_image_path && (
                  <button
                    onClick={() => setShowSolution(!showSolution)}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition"
                  >
                    {showSolution ? 'Шешімді жасыру' : '🔎 Шешімін көру'}
                  </button>
                )}
                <button
                  onClick={fetchRandomTask}
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-2 px-4 rounded-lg transition shadow-lg"
                >
                  Келесі есеп →
                </button>
              </div>
            </div>
          )}

          {showSolution && checkResult?.solution_image_path && (
            <div className="mb-6">
              <h3 className="text-xl font-bold text-gray-800 mb-3">📝 Шешімі:</h3>
              <img
                src={`${apiUrl}/${checkResult.solution_image_path}`}
                alt="Шешімі"
                className="w-full rounded-lg shadow-md"
              />
            </div>
          )}
        </div>

        <div className="mt-6 text-center">
          <a
            href="/"
            className="text-blue-600 hover:text-blue-800 font-semibold underline"
          >
            ← Басты бетке қайту
          </a>
        </div>
      </div>
    </div>
  );
}
