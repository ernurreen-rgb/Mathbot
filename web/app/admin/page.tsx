// web/app/admin/page.tsx
"use client";

import { useState, useEffect, useCallback } from "react";
import { useSession, signIn } from "next-auth/react";

interface Task {
  id: number;
  image_path: string;
  correct_option: string;
  answer_type: string;
  solution_image_path?: string;
  created_at?: string;
  created_by?: number;
  task_text?: string;
  solution_text?: string;
}

interface TasksResponse {
  tasks: Task[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export default function AdminPage() {
  const { data: session, status } = useSession();
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const checkAdminStatus = useCallback(async () => {
    if (!session?.user?.email) {
      setIsAdmin(false);
      return;
    }

    try {
      const res = await fetch(`${apiUrl}/api/admin/verify`, {
        headers: {
          "X-Admin-Email": session.user.email,
        },
      });
      const data = await res.json();
      setIsAdmin(data.is_admin);
      // Debug logging (check browser console)
      if (!data.is_admin) {
        console.log("Admin verify failed - Your email:", session.user.email);
      }
    } catch {
      setIsAdmin(false);
    }
  }, [session?.user?.email, apiUrl]);

  const fetchTasks = useCallback(async () => {
    if (!session?.user?.email || !isAdmin) return;

    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiUrl}/api/admin/tasks?page=${page}&limit=10`, {
        headers: {
          "X-Admin-Email": session.user.email,
        },
      });
      
      if (!res.ok) {
        throw new Error(`Қате: ${res.status}`);
      }
      
      const data: TasksResponse = await res.json();
      setTasks(data.tasks);
      setTotalPages(data.total_pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Есептерді жүктеу қатесі");
    } finally {
      setLoading(false);
    }
  }, [apiUrl, session?.user?.email, isAdmin, page]);

  useEffect(() => {
    if (status !== "loading") {
      checkAdminStatus();
    }
  }, [status, checkAdminStatus]);

  useEffect(() => {
    if (isAdmin === true) {
      fetchTasks();
    }
  }, [isAdmin, page, fetchTasks]);

  const handleDelete = async (taskId: number) => {
    if (!confirm("Бұл есепті жоюға сенімдісіз бе?")) return;

    try {
      const res = await fetch(`${apiUrl}/api/admin/tasks/${taskId}`, {
        method: "DELETE",
        headers: {
          "X-Admin-Email": session?.user?.email || "",
        },
      });

      if (!res.ok) {
        throw new Error(`Жою қатесі: ${res.status}`);
      }

      setSuccessMessage("Есеп сәтті жойылды");
      fetchTasks();
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Жою қатесі");
    }
  };

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Жүктелуде...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 px-4">
        <div className="text-center max-w-md p-8 bg-white rounded-2xl shadow-xl">
          <h1 className="text-3xl font-bold text-gray-800 mb-4">🔐 Әкімші панелі</h1>
          <p className="text-gray-600 mb-6">Әкімші панеліне кіру үшін аккаунтыңызбен кіріңіз.</p>
          <button
            onClick={() => signIn("google")}
            className="flex items-center justify-center gap-2 w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
            </svg>
            Google арқылы кіру
          </button>
        </div>
      </div>
    );
  }

  if (isAdmin === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Тексерілуде...</p>
        </div>
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 px-4">
        <div className="text-center max-w-md p-8 bg-white rounded-2xl shadow-xl">
          <h1 className="text-3xl font-bold text-red-600 mb-4">⛔ Қатынас жоқ</h1>
          <p className="text-gray-600 mb-4">
            Бұл бетке тек әкімшілер кіре алады.
          </p>
          <p className="text-sm text-gray-500 mb-6">
            Сіздің email: {session.user?.email}
          </p>
          <a
            href="/"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg transition"
          >
            Басты бетке қайту
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">🔧 Әкімші панелі</h1>
              <p className="text-gray-600">Есептерді басқару</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowCreateForm(true);
                  setEditingTask(null);
                }}
                className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-semibold py-2 px-6 rounded-lg transition shadow-lg"
              >
                ➕ Жаңа есеп
              </button>
              <a
                href="/"
                className="bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2 px-6 rounded-lg transition"
              >
                ← Шығу
              </a>
            </div>
          </div>
        </div>

        {/* Messages */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
            <button onClick={() => setError(null)} className="float-right font-bold">×</button>
          </div>
        )}
        {successMessage && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg mb-6">
            {successMessage}
          </div>
        )}

        {/* Create/Edit Form Modal */}
        {(showCreateForm || editingTask) && (
          <TaskForm
            task={editingTask}
            apiUrl={apiUrl}
            email={session.user?.email || ""}
            onClose={() => {
              setShowCreateForm(false);
              setEditingTask(null);
            }}
            onSuccess={() => {
              setShowCreateForm(false);
              setEditingTask(null);
              fetchTasks();
              setSuccessMessage(editingTask ? "Есеп сәтті жаңартылды" : "Есеп сәтті қосылды");
              setTimeout(() => setSuccessMessage(null), 3000);
            }}
            onError={(msg) => setError(msg)}
          />
        )}

        {/* Tasks List */}
        <div className="bg-white rounded-2xl shadow-xl p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">📋 Есептер тізімі</h2>
          
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Жүктелуде...</p>
            </div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600">Әзірше есептер жоқ</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b-2 border-gray-200">
                      <th className="text-left py-3 px-4">ID</th>
                      <th className="text-left py-3 px-4">Сурет</th>
                      <th className="text-left py-3 px-4">Түрі</th>
                      <th className="text-left py-3 px-4">Жауап</th>
                      <th className="text-left py-3 px-4">Әрекеттер</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tasks.map((task) => (
                      <tr key={task.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 font-medium">#{task.id}</td>
                        <td className="py-3 px-4">
                          <img
                            src={`${apiUrl}/${task.image_path}`}
                            alt={`Есеп ${task.id}`}
                            className="w-24 h-16 object-cover rounded-lg shadow"
                          />
                        </td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-1 rounded-full text-sm font-medium ${
                            task.answer_type === "quiz" 
                              ? "bg-blue-100 text-blue-700" 
                              : "bg-purple-100 text-purple-700"
                          }`}>
                            {task.answer_type === "quiz" ? "Тест" : "Мәтін"}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono font-bold text-lg">
                          {task.correct_option}
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex gap-2">
                            <button
                              onClick={() => setEditingTask(task)}
                              className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded-lg text-sm transition"
                            >
                              ✏️ Өзгерту
                            </button>
                            <button
                              onClick={() => handleDelete(task.id)}
                              className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-lg text-sm transition"
                            >
                              🗑️ Жою
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-4 mt-6">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed px-4 py-2 rounded-lg transition"
                  >
                    ← Алдыңғы
                  </button>
                  <span className="text-gray-600">
                    {page} / {totalPages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed px-4 py-2 rounded-lg transition"
                  >
                    Келесі →
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// Task Create/Edit Form Component
interface TaskFormProps {
  task: Task | null;
  apiUrl: string;
  email: string;
  onClose: () => void;
  onSuccess: () => void;
  onError: (msg: string) => void;
}

function TaskForm({ task, apiUrl, email, onClose, onSuccess, onError }: TaskFormProps) {
  const [answerType, setAnswerType] = useState(task?.answer_type || "quiz");
  const [correctOption, setCorrectOption] = useState(task?.correct_option || "");
  const [taskImage, setTaskImage] = useState<File | null>(null);
  const [solutionImage, setSolutionImage] = useState<File | null>(null);
  const [taskText, setTaskText] = useState(task?.task_text || "");
  const [solutionText, setSolutionText] = useState(task?.solution_text || "");
  const [submitting, setSubmitting] = useState(false);
  const [taskImagePreview, setTaskImagePreview] = useState<string | null>(
    task?.image_path ? `${apiUrl}/${task.image_path}` : null
  );
  const [solutionImagePreview, setSolutionImagePreview] = useState<string | null>(
    task?.solution_image_path ? `${apiUrl}/${task.solution_image_path}` : null
  );

  const handleTaskImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setTaskImage(file);
      setTaskImagePreview(URL.createObjectURL(file));
    }
  };

  const handleSolutionImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSolutionImage(file);
      setSolutionImagePreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const formData = new FormData();
      
      if (task) {
        // Update existing task
        if (taskImage) formData.append("task_image", taskImage);
        if (solutionImage) formData.append("solution_image", solutionImage);
        if (correctOption) formData.append("correct_option", correctOption);
        if (answerType) formData.append("answer_type", answerType);
        // Always append text fields for updates (empty string is valid)
        formData.append("task_text", taskText);
        formData.append("solution_text", solutionText);

        const res = await fetch(`${apiUrl}/api/admin/tasks/${task.id}`, {
          method: "PUT",
          headers: {
            "X-Admin-Email": email,
          },
          body: formData,
        });

        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || "Жаңарту қатесі");
        }
      } else {
        // Create new task
        if (!taskText && !taskImage) {
          throw new Error("Есеп мәтінін немесе суретін жүктеңіз");
        }
        if (!correctOption) {
          throw new Error("Дұрыс жауапты енгізіңіз");
        }

        if (taskImage) formData.append("task_image", taskImage);
        if (solutionImage) formData.append("solution_image", solutionImage);
        formData.append("correct_option", correctOption);
        formData.append("answer_type", answerType);
        formData.append("task_text", taskText);
        formData.append("solution_text", solutionText);

        const res = await fetch(`${apiUrl}/api/admin/tasks`, {
          method: "POST",
          headers: {
            "X-Admin-Email": email,
          },
          body: formData,
        });

        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || "Қосу қатесі");
        }
      }

      onSuccess();
    } catch (err) {
      onError(err instanceof Error ? err.message : "Қате болды");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800">
              {task ? "✏️ Есепті өзгерту" : "➕ Жаңа есеп қосу"}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Answer Type */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">
                Есеп түрі
              </label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="answer_type"
                    value="quiz"
                    checked={answerType === "quiz"}
                    onChange={(e) => setAnswerType(e.target.value)}
                    className="w-4 h-4"
                  />
                  <span>Тест (A/B/C/D)</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="answer_type"
                    value="text"
                    checked={answerType === "text"}
                    onChange={(e) => setAnswerType(e.target.value)}
                    className="w-4 h-4"
                  />
                  <span>Қолмен енгізу</span>
                </label>
              </div>
            </div>

            {/* Correct Answer */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">
                Дұрыс жауап
              </label>
              {answerType === "quiz" ? (
                <div className="flex gap-2">
                  {["A", "B", "C", "D"].map((option) => (
                    <button
                      key={option}
                      type="button"
                      onClick={() => setCorrectOption(option)}
                      className={`px-6 py-3 rounded-lg font-bold transition ${
                        correctOption === option
                          ? "bg-blue-600 text-white"
                          : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                      }`}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              ) : (
                <input
                  type="text"
                  value={correctOption}
                  onChange={(e) => setCorrectOption(e.target.value)}
                  placeholder="Жауапты енгізіңіз"
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
                />
              )}
            </div>

            {/* Task Text (LaTeX/Plain text) */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">
                Есеп мәтіні (LaTeX немесе қарапайым мәтін) {!task && <span className="text-red-500">*</span>}
              </label>
              <textarea
                value={taskText}
                onChange={(e) => setTaskText(e.target.value)}
                placeholder="Есепті мәтін форматында енгізіңіз. LaTeX үшін $ $ немесе $$ $$ қолданыңыз"
                rows={6}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none font-mono"
              />
              <p className="text-sm text-gray-500 mt-1">
                LaTeX мысалы: $x^2 + y^2 = r^2$ немесе $$\int_0^1 x^2 dx$$
              </p>
            </div>

            {/* Task Image (Optional) */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">
                Есеп суреті (міндетті емес)
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={handleTaskImageChange}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
              />
              {taskImagePreview && (
                <div className="mt-2">
                  <img
                    src={taskImagePreview}
                    alt="Есеп"
                    className="max-w-full max-h-48 rounded-lg shadow"
                  />
                </div>
              )}
            </div>

            {/* Solution Text (LaTeX/Plain text) */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">
                Шешім мәтіні (LaTeX немесе қарапайым мәтін)
              </label>
              <textarea
                value={solutionText}
                onChange={(e) => setSolutionText(e.target.value)}
                placeholder="Шешімді мәтін форматында енгізіңіз"
                rows={6}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none font-mono"
              />
            </div>

            {/* Solution Image (Optional) */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">
                Шешім суреті (міндетті емес)
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={handleSolutionImageChange}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
              />
              {solutionImagePreview && (
                <div className="mt-2">
                  <img
                    src={solutionImagePreview}
                    alt="Шешім"
                    className="max-w-full max-h-48 rounded-lg shadow"
                  />
                </div>
              )}
            </div>

            {/* Submit Buttons */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={submitting}
                className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 text-white font-bold py-3 px-6 rounded-lg transition shadow-lg"
              >
                {submitting ? "Жүктелуде..." : task ? "Сақтау" : "Қосу"}
              </button>
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-lg transition"
              >
                Бас тарту
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}