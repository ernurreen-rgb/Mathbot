// web/components/TaskCard.tsx
"use client";
import { useState } from "react";

interface TaskCardTask {
  image_path: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function buildAssetUrl(path: string) {
  if (path.startsWith("http")) return path;
  return `${API_URL}/${path.replace(/^[\\/]+/, "")}`;
}

function getErrorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Белгісіз қате";
}

export default function TaskCard() {
  const [task, setTask] = useState<TaskCardTask | null>(null);

  const getTask = async () => {
    try {
      const res = await fetch(`${API_URL}/api/task/random`);
      if (!res.ok) throw new Error("Не удалось получить задачу");
      const data = await res.json();
      setTask(data);
    } catch (error) {
      alert("Ошибка при получении задачи: " + getErrorMessage(error));
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
            src={buildAssetUrl(task.image_path)}
            alt="Есеп"
            className="rounded-lg shadow-md"
          />
          {/* Жауап беру формасы */}
        </div>
      )}
    </div>
  );
}