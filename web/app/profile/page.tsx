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

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlocked: boolean;
  unlocked_at?: string;
}

const leagueNames: Record<string, string> = {
  bronze: "🥉 Қола",
  silver: "🥈 Күміс",
  gold: "🥇 Алтын",
};

const leagueColors: Record<string, string> = {
  bronze: "from-orange-400 to-amber-500",
  silver: "from-gray-300 to-slate-400",
  gold: "from-yellow-400 to-amber-500",
};

// Calculate user level based on points
function calculateLevel(points: number): { level: number; progress: number; nextLevelPoints: number } {
  // Each level requires more points: level 1 = 0, level 2 = 10, level 3 = 25, level 4 = 50, etc.
  const levelThresholds = [0, 10, 25, 50, 100, 200, 350, 550, 800, 1100, 1500, 2000, 2600, 3300, 4100, 5000];
  
  let level = 1;
  for (let i = 1; i < levelThresholds.length; i++) {
    if (points >= levelThresholds[i]) {
      level = i + 1;
    } else {
      break;
    }
  }
  
  const currentThreshold = levelThresholds[level - 1] || 0;
  const nextThreshold = levelThresholds[level] || levelThresholds[levelThresholds.length - 1] + 1000;
  const progress = ((points - currentThreshold) / (nextThreshold - currentThreshold)) * 100;
  
  return { level, progress: Math.min(progress, 100), nextLevelPoints: nextThreshold };
}

// Extract short name from achievement (removes emoji prefix if present)
function getAchievementShortName(name: string): string {
  if (!name) return "";
  // Split by space and take all parts after the first (emoji) if there are multiple parts
  const parts = name.split(" ");
  if (parts.length > 1) {
    return parts.slice(1).join(" ");
  }
  return name;
}

export default function ProfilePage() {
  const { data: session, status } = useSession();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
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
      const [statsRes, achievementsRes] = await Promise.all([
        fetch(`${apiUrl}/api/user/web/${encodeURIComponent(session.user.email)}`),
        fetch(`${apiUrl}/api/user/web/${encodeURIComponent(session.user.email)}/achievements`)
      ]);
      
      if (!statsRes.ok) {
        throw new Error("Профильді жүктеу мүмкін болмады");
      }
      const data = await statsRes.json();
      setStats(data);
      setNickname(data.nickname || "");
      
      if (achievementsRes.ok) {
        const achievementsData = await achievementsRes.json();
        setAchievements(achievementsData.achievements || []);
      }
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
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 via-white to-slate-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mx-auto mb-4"></div>
          <p className="text-xl text-slate-600">Жүктелуде...</p>
        </div>
      </div>
    );
  }

  // Show sign in page if not authenticated
  if (status === "unauthenticated") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-100 via-white to-slate-100 py-12 px-4">
        <div className="max-w-md mx-auto">
          <div className="bg-white rounded-3xl shadow-2xl p-8 border border-slate-200">
            <h1 className="text-3xl font-bold text-slate-800 mb-8 text-center">
              👤 Профиль
            </h1>

            <div className="text-center py-8">
              <div className="text-6xl mb-4">🔐</div>
              <h2 className="text-xl font-bold text-slate-800 mb-3">
                Профильді көру үшін кіріңіз
              </h2>
              <p className="text-slate-600 mb-6 text-sm">
                Google арқылы кіріп, ұпай жинап, рейтингте көріне аласыз
              </p>
              <div className="space-y-4">
                <button
                  onClick={() => signIn("google")}
                  className="w-full flex items-center justify-center gap-3 bg-white hover:bg-gray-100 text-gray-700 font-bold py-3 px-6 rounded-xl transition shadow-lg border border-slate-200"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                  </svg>
                  Google арқылы кіру
                </button>
                <a
                  href="/"
                  className="block w-full bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold py-3 px-6 rounded-xl transition text-center"
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

  const levelInfo = stats ? calculateLevel(stats.points) : { level: 1, progress: 0, nextLevelPoints: 10 };
  const unlockedCount = achievements.filter(a => a.unlocked).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-white to-slate-100 py-8 px-4">
      <div className="max-w-2xl mx-auto space-y-6">
        
        {/* Profile Header Card */}
        <div className="bg-white rounded-3xl shadow-2xl p-6 border border-slate-200 relative overflow-hidden">
          {/* Decorative background */}
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-100 to-slate-100 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-br from-slate-100 to-gray-100 rounded-full blur-2xl"></div>
          
          <div className="relative">
            {/* Sign out button */}
            <button
              onClick={() => signOut()}
              className="absolute top-0 right-0 text-red-400 hover:text-red-300 text-sm font-semibold transition"
            >
              Шығу
            </button>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded-xl text-red-600 text-sm">
                {error}
              </div>
            )}

            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-500 mx-auto mb-4"></div>
                <p className="text-slate-600">Жүктелуде...</p>
              </div>
            ) : stats ? (
              <div className="space-y-6">
                {/* Avatar and User Info */}
                <div className="flex flex-col items-center text-center">
                  {/* Avatar with level ring */}
                  <div className="relative mb-4">
                    <div className={`absolute inset-0 rounded-full bg-gradient-to-r ${leagueColors[stats.league || "bronze"]} p-1 animate-pulse`}>
                      <div className="w-full h-full rounded-full bg-white"></div>
                    </div>
                    <div className="relative p-1">
                      {session?.user?.image ? (
                        <img
                          src={session.user.image}
                          alt="Profile"
                          className="w-24 h-24 rounded-full border-4 border-white"
                        />
                      ) : (
                        <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-slate-500 flex items-center justify-center text-4xl">
                          👤
                        </div>
                      )}
                    </div>
                    {/* Level badge */}
                    <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-blue-500 to-slate-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
                      LVL {levelInfo.level}
                    </div>
                  </div>

                  {/* Name */}
                  <h2 className="text-2xl font-bold text-slate-800 mb-1">
                    {stats.nickname || session?.user?.name || stats.name}
                  </h2>
                  <p className="text-slate-500 text-sm mb-3">{session?.user?.email}</p>

                  {/* League Badge */}
                  <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r ${leagueColors[stats.league || "bronze"]} text-white font-semibold shadow-lg`}>
                    {leagueNames[stats.league || "bronze"] || "🥉 Қола"}
                  </div>
                </div>

                {/* Level Progress Bar */}
                <div className="bg-slate-50 rounded-xl p-4">
                  <div className="flex justify-between text-sm text-slate-600 mb-2">
                    <span>Деңгей {levelInfo.level}</span>
                    <span>{stats.points} / {levelInfo.nextLevelPoints} ұпай</span>
                  </div>
                  <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 via-slate-500 to-gray-600 rounded-full transition-all duration-500"
                      style={{ width: `${levelInfo.progress}%` }}
                    ></div>
                  </div>
                </div>

                {/* Nickname Section */}
                <div className="bg-slate-50 rounded-xl p-4">
                  {isEditingNickname ? (
                    <div className="space-y-2">
                      <input
                        type="text"
                        value={nickname}
                        onChange={(e) => setNickname(e.target.value)}
                        placeholder="Никнейм енгізіңіз"
                        maxLength={30}
                        className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg text-slate-800 placeholder-slate-400 focus:border-blue-500 focus:outline-none"
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={handleUpdateNickname}
                          className="flex-1 bg-blue-500 hover:bg-blue-600 text-white py-2 rounded-lg transition font-semibold"
                        >
                          Сақтау
                        </button>
                        <button
                          onClick={() => {
                            setIsEditingNickname(false);
                            setNickname(stats.nickname || "");
                            setNicknameError(null);
                          }}
                          className="px-4 text-slate-500 hover:text-slate-800 transition"
                        >
                          Болдырмау
                        </button>
                      </div>
                      {nicknameError && (
                        <p className="text-red-400 text-sm">{nicknameError}</p>
                      )}
                    </div>
                  ) : (
                    <button
                      onClick={() => setIsEditingNickname(true)}
                      className="w-full text-slate-500 hover:text-slate-800 text-sm transition flex items-center justify-center gap-2"
                    >
                      ✏️ {stats.nickname ? "Никнеймді өзгерту" : "Никнейм қосу (рейтингте көріну үшін)"}
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-slate-600">
                Профиль деректері табылмады
              </div>
            )}
          </div>
        </div>

        {/* Stats Grid */}
        {stats && (
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-lg text-center">
              <p className="text-3xl font-bold text-yellow-500">{stats.points}</p>
              <p className="text-slate-500 text-sm mt-1">💎 Жалпы ұпай</p>
            </div>
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-lg text-center">
              <p className="text-3xl font-bold text-green-500">{stats.solved_count}</p>
              <p className="text-slate-500 text-sm mt-1">🧩 Шешілген есептер</p>
            </div>
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-lg text-center">
              <p className="text-3xl font-bold text-blue-500">{stats.weekly_points || 0}</p>
              <p className="text-slate-500 text-sm mt-1">⚡ Апталық ұпай</p>
            </div>
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-lg text-center">
              <p className="text-3xl font-bold text-indigo-500">{unlockedCount}</p>
              <p className="text-slate-500 text-sm mt-1">🏅 Жетістіктер</p>
            </div>
          </div>
        )}

        {/* Achievements Section */}
        {achievements.length > 0 && (
          <div className="bg-white rounded-3xl shadow-2xl p-6 border border-slate-200">
            <h3 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
              🏅 Жетістіктер
              <span className="text-sm font-normal text-slate-500">
                ({unlockedCount}/{achievements.length})
              </span>
            </h3>
            
            <div className="grid grid-cols-3 gap-3">
              {achievements.map((achievement) => (
                <div
                  key={achievement.id}
                  className={`relative p-3 rounded-xl text-center transition-all ${
                    achievement.unlocked
                      ? "bg-gradient-to-br from-blue-100 to-slate-100 border border-blue-300"
                      : "bg-slate-50 border border-slate-200 opacity-50 grayscale"
                  }`}
                  title={achievement.description}
                >
                  <div className="text-3xl mb-1">{achievement.icon}</div>
                  <p className="text-xs text-slate-700 font-medium truncate">{getAchievementShortName(achievement.name)}</p>
                  {achievement.unlocked && (
                    <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-xs">✓</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="grid grid-cols-3 gap-3">
          <a
            href="/tasks"
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-4 rounded-xl transition shadow-lg text-center text-sm"
          >
            🧩 Есеп шешу
          </a>
          <a
            href="/leagues"
            className="bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white font-bold py-4 px-4 rounded-xl transition shadow-lg text-center text-sm"
          >
            🏆 Лигалар
          </a>
          <a
            href="/rating"
            className="bg-gradient-to-r from-slate-600 to-gray-600 hover:from-slate-700 hover:to-gray-700 text-white font-bold py-4 px-4 rounded-xl transition shadow-lg text-center text-sm"
          >
            📊 Рейтинг
          </a>
        </div>

        {/* Back button */}
        <div className="text-center">
          <a
            href="/"
            className="text-slate-500 hover:text-slate-800 font-semibold transition"
          >
            ← Басты бетке қайту
          </a>
        </div>
      </div>
    </div>
  );
}
