// web/app/tasks/page.tsx
"use client";

import { useState, useEffect } from "react";
import Image from "next/image";

interface Task {
  id: number;
  image_path: string;
  answer_type: string;
  solution_image_path?: string;
}

export default function TasksPage() {
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRandomTask();
  }, []);

  const fetchRandomTask = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/api/task/random");
      if (!res.ok) {
        throw new Error("Есептер табылмады");
      }
      const data = await res.json();
      setTask(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Қате болды");
    } finally {
      setLoading(false);
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
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="text-center max-w-md p-8 bg-white rounded-2xl shadow-xl">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Қате</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={fetchRandomTask}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition"
          >
            Қайталап көру
          </button>
        </div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="text-center max-w-md p-8 bg-white rounded-2xl shadow-xl">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Есептер жоқ</h2>
          <p className="text-gray-600">Әзірге шешуге есептер қосылмаған</p>
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
              src={`http://localhost:8000/${task.image_path}`}
              alt={`Есеп ${task.id}`}
              className="w-full rounded-lg shadow-md"
            />
          </div>

          <div className="text-center">
            <p className="text-gray-600 mb-4">
              Telegram ботында шешу үшін: <span className="font-mono bg-gray-100 px-3 py-1 rounded">@yeramathbot</span>
            </p>
            <button
              onClick={fetchRandomTask}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-3 px-8 rounded-lg transition shadow-lg"
            >
              Келесі есеп →
            </button>
          </div>
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
