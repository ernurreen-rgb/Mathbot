// web/component/TaskCard.tsx
"use client";
import { useState } from "react";

export default function TaskCard() {
  const [task, setTask] = useState<any>(null);

  // URL FastAPI backend (production)
  const API_URL = "https://mathbot-nu.vercel.app";

  const getTask = async () => {
    try {
      const res = await fetch(API_URL);
      if (!res.ok) throw new Error("Не удалось получить задачу");
      const data = await res.json();
      setTask(data);
    } catch (e) {
      alert("Ошибка при получении задачи: " + (e as Error).message);
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-xl p-8">
      <button onClick={getTask} className="bg-blue-600 text-white px-8 py-4 rounded-xl text-xl font-bold hover:bg-blue-700">
        Келесі есеп алу
      </button>

      {task && (
        <div className="mt-8">
          <img
            src={
              task.image_path.startsWith("http")
                ? task.image_path
                : `https://mathbot-nu.vercel.app/${task.image_path.replace(/^\\|^\//, "")}`
            }
            alt="Есеп"
            className="rounded-lg shadow-md"
          />
          {/* Жауап беру формасы */}
        </div>
      )}
    </div>
  );
}