// web/component/TaskCard.tsx
"use client";
import { useState } from "react";

export default function TaskCard() {
  const [task, setTask] = useState<any>(null);

  const getTask = async () => {
    const res = await fetch("/api/task/random");
    const data = await res.json();
    setTask(data);
  };

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-xl p-8">
      <button onClick={getTask} className="bg-blue-600 text-white px-8 py-4 rounded-xl text-xl font-bold hover:bg-blue-700">
        Келесі есеп алу
      </button>

      {task && (
        <div className="mt-8">
          <img src={`/images/task_${task.id}.jpg`} alt="Есеп" className="rounded-lg shadow-md" />
          {/* Жауап беру формасы */}
        </div>
      )}
    </div>
  );
}