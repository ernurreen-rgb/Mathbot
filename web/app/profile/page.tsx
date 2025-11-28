// web/app/profile/page.tsx
"use client";

import { useState, useEffect, useCallback } from "react";
import { useSession, signIn, signOut } from "next-auth/react";

interface UserStats {
  email?: string;
  name?: string;
  nickname?: string | null;
  points: number;
  solved_count: number;
  weekly_points?: number;
  league?: string;
  registration_date?: string;
}

const leagueNames: Record<string, string> = {
  bronze: "🥉 Қола",
  silver: "🥈 Күміс",
  gold: "🥇 Алтын",
};

export default function ProfilePage() {
  const { data: session, status } = useSession();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nickname, setNickname] = useState("");
  const [isEditingNickname, setIsEditingNickname] = useState(false);
  const [nicknameError, setNicknameError] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchUserStats = useCallback(async () => {
    if (!session?.user?.email) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(
        `${apiUrl}/api/user/web/${encodeURIComponent(session.user.email)}`
      );
      if (!res.ok) {
        throw new Error("Профильді жүктеу мүмкін болмады");
      }
      const data = await res.json();
      setStats(data);
      setNickname(data.nickname || "");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Қате болды");
    } finally {
      setLoading(false);
    }
  }, [session?.user?.email, apiUrl]);

  useEffect(() => {
    if (status === "authenticated") {
      fetchUserStats();
    }
  }, [status, fetchUserStats]);

  const handleUpdateNickname = async () => {
    if (!session?.user?.email) return;

    setNicknameError(null);

    try {
      const res = await fetch(`${apiUrl}/api/user/web/nickname`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: session.user.email,
          nickname: nickname.trim(),
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Никнеймді сақтау мүмкін болмады");
      }

      const data = await res.json();
      setStats(data);
      setIsEditingNickname(false);
    } catch (err) {
      setNicknameError(err instanceof Error ? err.message : "Қате болды");
    }
  };

  // Show loading state
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

  // Show sign in page if not authenticated
  if (status === "unauthenticated") {
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
                Профильді көру үшін кіріңіз
              </h2>
              <p className="text-gray-600 mb-6">
                Google арқылы кіріп, ұпай жинап, рейтингте көріне аласыз
              </p>
              <div className="space-y-4">
                <button
                  onClick={() => signIn("google")}
                  className="inline-flex items-center gap-3 bg-white border-2 border-gray-200 hover:border-gray-300 text-gray-700 font-bold py-3 px-8 rounded-lg transition shadow-lg"
                >
                  <svg className="w-6 h-6" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  Google арқылы кіру
                </button>
                <br />
                <a
                  href="/"
                  className="inline-block bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 text-white font-bold py-3 px-8 rounded-lg transition shadow-lg"
                >
                  ← Басты бетке қайту
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800">👤 Профиль</h1>
            <button
              onClick={() => signOut()}
              className="text-red-600 hover:text-red-800 font-semibold"
            >
              Шығу
            </button>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-100 border border-red-400 rounded-lg text-red-700">
              {error}
            </div>
          )}

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Жүктелуде...</p>
            </div>
          ) : stats ? (
            <div className="space-y-6">
              {/* User Info */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6">
                <div className="flex items-center gap-4 mb-4">
                  {session?.user?.image && (
                    <img
                      src={session.user.image}
                      alt="Profile"
                      className="w-16 h-16 rounded-full"
                    />
                  )}
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800">
                      {stats.nickname || session?.user?.name || stats.name}
                    </h2>
                    <p className="text-gray-600">{session?.user?.email}</p>
                  </div>
                </div>

                {/* Nickname Section */}
                <div className="mt-4">
                  {isEditingNickname ? (
                    <div className="flex gap-2 items-center">
                      <input
                        type="text"
                        value={nickname}
                        onChange={(e) => setNickname(e.target.value)}
                        placeholder="Никнейм енгізіңіз"
                        maxLength={30}
                        className="flex-1 px-3 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
                      />
                      <button
                        onClick={handleUpdateNickname}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
                      >
                        Сақтау
                      </button>
                      <button
                        onClick={() => {
                          setIsEditingNickname(false);
                          setNickname(stats.nickname || "");
                          setNicknameError(null);
                        }}
                        className="text-gray-600 hover:text-gray-800 px-2"
                      >
                        Болдырмау
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setIsEditingNickname(true)}
                      className="text-blue-600 hover:text-blue-800 text-sm underline"
                    >
                      {stats.nickname
                        ? "Никнеймді өзгерту"
                        : "Никнейм қосу (рейтингте көріну үшін)"}
                    </button>
                  )}
                  {nicknameError && (
                    <p className="text-red-500 text-sm mt-1">{nicknameError}</p>
                  )}
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-r from-yellow-400 to-orange-500 rounded-xl p-4 text-white text-center">
                  <p className="text-3xl font-bold">{stats.points}</p>
                  <p className="text-sm opacity-90">Жалпы ұпай</p>
                </div>
                <div className="bg-gradient-to-r from-green-400 to-emerald-500 rounded-xl p-4 text-white text-center">
                  <p className="text-3xl font-bold">{stats.solved_count}</p>
                  <p className="text-sm opacity-90">Шешілген есептер</p>
                </div>
                <div className="bg-gradient-to-r from-blue-400 to-indigo-500 rounded-xl p-4 text-white text-center">
                  <p className="text-3xl font-bold">{stats.weekly_points || 0}</p>
                  <p className="text-sm opacity-90">Апталық ұпай</p>
                </div>
                <div className="bg-gradient-to-r from-purple-400 to-pink-500 rounded-xl p-4 text-white text-center">
                  <p className="text-2xl font-bold">
                    {leagueNames[stats.league || "bronze"] || "🥉 Қола"}
                  </p>
                  <p className="text-sm opacity-90">Лига</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-wrap gap-4 justify-center pt-4">
                <a
                  href="/tasks"
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-3 px-8 rounded-lg transition shadow-lg"
                >
                  🧩 Есеп шешу
                </a>
                <a
                  href="/leagues"
                  className="bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white font-bold py-3 px-8 rounded-lg transition shadow-lg"
                >
                  🏆 Лигалар
                </a>
                <a
                  href="/rating"
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 px-8 rounded-lg transition shadow-lg"
                >
                  📊 Рейтинг
                </a>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-600">
              Профиль деректері табылмады
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
