// web/app/profile/page.tsx
"use client";

import { useSession } from "next-auth/react";
import { useState, useEffect, useCallback } from "react";

interface UserStats {
  email?: string;
  name?: string;
  nickname?: string | null;
  points: number;
  solved_count: number;
  registration_date?: string;
}

export default function ProfilePage() {
  const { data: session } = useSession();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditingNickname, setIsEditingNickname] = useState(false);
  const [nicknameInput, setNicknameInput] = useState("");
  const [nicknameSaving, setNicknameSaving] = useState(false);
  const [nicknameError, setNicknameError] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchUserStats = useCallback(async () => {
    if (!session?.user?.email) return;
    
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiUrl}/api/user/web/${encodeURIComponent(session.user.email)}`);
      if (!res.ok) {
        throw new Error(`Сервер қатесі: ${res.status}`);
      }
      const data = await res.json();
      setStats(data);
    } catch (err) {
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError(`API серверіне қосылу мүмкін емес.\n\nBot серверін іске қосыңыз:\ncd bot && python main.py\n\nСервер: ${apiUrl}`);
      } else {
        setError(err instanceof Error ? err.message : "Қате болды");
      }
    } finally {
      setLoading(false);
    }
  }, [session?.user?.email, apiUrl]);

  const updateNickname = async () => {
    if (!session?.user?.email) return;
    
    setNicknameSaving(true);
    setNicknameError(null);
    try {
      const res = await fetch(`${apiUrl}/api/user/web/nickname`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: session.user.email,
          nickname: nicknameInput.trim()
        })
      });
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: `Сервер қатесі: ${res.status}` }));
        throw new Error(errorData.detail || `Сервер қатесі: ${res.status}`);
      }
      
      const data = await res.json();
      setStats(data);
      setIsEditingNickname(false);
    } catch (err) {
      setNicknameError(err instanceof Error ? err.message : "Никнеймді сақтау қатесі");
    } finally {
      setNicknameSaving(false);
    }
  };

  useEffect(() => {
    if (session?.user?.email) {
      fetchUserStats();
    }
  }, [session?.user?.email, fetchUserStats]);

  useEffect(() => {
    if (stats?.nickname) {
      setNicknameInput(stats.nickname);
    }
  }, [stats?.nickname]);

  if (!session) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-2xl p-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center">
              👤 Профиль
            </h1>

            <div className="text-center py-12">
              <div className="text-6xl mb-4">🔐</div>
              <h2 className="text-2xl font-bold text-gray-800 mb-3">
                Кіру керек
              </h2>
              <p className="text-gray-600 mb-6">
                Профильді көру үшін Google арқылы кіріңіз немесе Telegram ботына кіріңіз
              </p>
              <div className="space-y-4">
                <a
                  href="/"
                  className="inline-block bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-3 px-8 rounded-lg transition shadow-lg"
                >
                  ← Басты бетке қайту
                </a>
                <br />
                <a
                  href="https://t.me/yeramathbot"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-bold py-3 px-8 rounded-lg transition shadow-lg"
                >
                  Telegram ботын ашу →
                </a>
              </div>
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Профиль жүктелуде...</p>
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
              onClick={fetchUserStats}
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center">
            👤 Профиль
          </h1>

          <div className="space-y-6">
            {/* User info */}
            <div className="flex items-center gap-6 pb-6 border-b border-gray-200">
              {session.user.image && (
                <img
                  src={session.user.image}
                  alt={session.user.name || "User"}
                  className="w-20 h-20 rounded-full border-4 border-blue-200"
                />
              )}
              <div className="flex-1">
                <h2 className="text-3xl font-bold text-gray-800">
                  {session.user.name || stats?.name || "Қолданушы"}
                </h2>
                <p className="text-gray-600 text-lg">{session.user.email}</p>
              </div>
            </div>

            {/* Nickname Section */}
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-xl border-2 border-purple-200">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">✨</span>
                    <h3 className="text-lg font-bold text-gray-800">Никнейм (рейтингте көрінеді)</h3>
                  </div>
                  {!isEditingNickname ? (
                    <div className="flex items-center gap-3">
                      <p className="text-xl font-semibold text-purple-700">
                        {stats?.nickname || "Орнатылмаған"}
                      </p>
                      <button
                        onClick={() => setIsEditingNickname(true)}
                        className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-4 rounded-lg transition text-sm"
                      >
                        {stats?.nickname ? "✏️ Өзгерту" : "➕ Қосу"}
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <input
                        type="text"
                        value={nicknameInput}
                        onChange={(e) => setNicknameInput(e.target.value)}
                        placeholder="Никнеймді енгізіңіз"
                        className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:outline-none focus:border-purple-500"
                        maxLength={30}
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={updateNickname}
                          disabled={nicknameSaving || !nicknameInput.trim()}
                          className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded-lg transition"
                        >
                          {nicknameSaving ? "Сақталуда..." : "✅ Сақтау"}
                        </button>
                        <button
                          onClick={() => {
                            setIsEditingNickname(false);
                            setNicknameInput(stats?.nickname || "");
                            setNicknameError(null);
                          }}
                          disabled={nicknameSaving}
                          className="bg-gray-500 hover:bg-gray-600 disabled:bg-gray-300 text-white font-semibold py-2 px-4 rounded-lg transition"
                        >
                          ❌ Болдырмау
                        </button>
                      </div>
                      {nicknameError && (
                        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded-lg text-sm">
                          ⚠️ {nicknameError}
                        </div>
                      )}
                    </div>
                  )}
                  {!stats?.nickname && !isEditingNickname && (
                    <p className="text-sm text-gray-600 mt-2">
                      💡 Никнейм орнатсаңыз, рейтингте email-дің орнына никнейм көрсетіледі
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border-2 border-blue-200">
                <div className="flex items-center gap-4">
                  <div className="text-5xl">💎</div>
                  <div>
                    <p className="text-gray-600 text-sm font-semibold">Ұпай</p>
                    <p className="text-4xl font-bold text-blue-600">{stats?.points || 0}</p>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-xl border-2 border-green-200">
                <div className="flex items-center gap-4">
                  <div className="text-5xl">🧩</div>
                  <div>
                    <p className="text-gray-600 text-sm font-semibold">Шешілгені</p>
                    <p className="text-4xl font-bold text-green-600">{stats?.solved_count || 0}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Registration date */}
            {stats?.registration_date && (
              <div className="text-center text-gray-500 text-sm pt-6 border-t border-gray-200">
                Тіркелген күні: {new Date(stats.registration_date).toLocaleDateString(undefined, {
                  day: "numeric",
                  month: "long",
                  year: "numeric"
                })}
              </div>
            )}

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-4 pt-6">
              <a
                href="/tasks"
                className="flex-1 text-center bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-3 px-6 rounded-lg transition shadow-lg"
              >
                🧩 Есеп шешу
              </a>
              <a
                href="/rating"
                className="flex-1 text-center bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 px-6 rounded-lg transition shadow-lg"
              >
                🏆 Рейтинг
              </a>
            </div>
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
