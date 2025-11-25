// web/app/leagues/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";

interface User {
  // Telegram users
  user_id?: number;
  username?: string | null;
  full_name?: string | null;
  // Web users
  email?: string;
  name?: string | null;
  nickname?: string | null;
  // Common fields
  points: number;
  solved_count: number;
  weekly_points: number;
  league: string;
  source: 'telegram' | 'web';
}

interface League {
  id: string;
  name: string;
}

interface LeagueInfo {
  league: string;
  weekly_points: number;
  points: number;
  rank?: number;
}

export default function LeaguesPage() {
  const { data: session } = useSession();
  const [leagues, setLeagues] = useState<League[]>([]);
  const [currentLeague, setCurrentLeague] = useState<string>("bronze");
  const [leagueUsers, setLeagueUsers] = useState<User[]>([]);
  const [userLeagueInfo, setUserLeagueInfo] = useState<LeagueInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetchLeagues();
  }, []);

  useEffect(() => {
    if (session?.user?.email) {
      fetchUserLeagueInfo();
    }
  }, [session?.user?.email]);

  useEffect(() => {
    if (currentLeague) {
      fetchLeagueLeaderboard(currentLeague);
    }
  }, [currentLeague]);

  const fetchLeagues = async () => {
    try {
      const res = await fetch(`${apiUrl}/api/leagues`);
      if (!res.ok) throw new Error(`Сервер қатесі: ${res.status}`);
      const data = await res.json();
      setLeagues(data.leagues || []);
    } catch (err) {
      console.error("Failed to fetch leagues:", err);
    }
  };

  const fetchUserLeagueInfo = async () => {
    if (!session?.user?.email) return;
    
    try {
      const res = await fetch(`${apiUrl}/api/user/web/${encodeURIComponent(session.user.email)}/league`);
      if (!res.ok) throw new Error(`Сервер қатесі: ${res.status}`);
      const data = await res.json();
      setUserLeagueInfo(data);
      setCurrentLeague(data.league || "bronze");
    } catch (err) {
      console.error("Failed to fetch user league info:", err);
    }
  };

  const fetchLeagueLeaderboard = async (league: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiUrl}/api/league/${league}?limit=30`);
      if (!res.ok) {
        throw new Error(`Сервер қатесі: ${res.status}`);
      }
      const data = await res.json();
      setLeagueUsers(data.users || []);
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

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 px-4">
        <div className="text-center max-w-2xl p-8 bg-white rounded-2xl shadow-xl">
          <h2 className="text-2xl font-bold text-red-600 mb-4">⚠️ Қате</h2>
          <pre className="text-left text-gray-700 mb-6 whitespace-pre-wrap bg-gray-50 p-4 rounded-lg border border-gray-200 text-sm">{error}</pre>
          <div className="space-y-3">
            <button
              onClick={() => fetchLeagueLeaderboard(currentLeague)}
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

  const getLeagueColor = (league: string) => {
    const colors: Record<string, string> = {
      bronze: "from-orange-100 to-amber-100 border-orange-300",
      silver: "from-gray-100 to-slate-100 border-gray-300",
      gold: "from-yellow-100 to-amber-100 border-yellow-400",
      platinum: "from-cyan-100 to-blue-100 border-cyan-400",
      diamond: "from-purple-100 to-pink-100 border-purple-400"
    };
    return colors[league] || colors.bronze;
  };

  const getPromotionZone = (position: number, total: number) => {
    if (position <= 3) return "promotion"; // Top 3 get promoted
    if (position > total - 3 && total > 6) return "demotion"; // Bottom 3 get demoted
    return "safe";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* User League Info */}
        {session && userLeagueInfo && (
          <div className={`bg-gradient-to-r ${getLeagueColor(userLeagueInfo.league)} border-2 rounded-2xl shadow-xl p-6 mb-8`}>
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">
                  {leagues.find(l => l.id === userLeagueInfo.league)?.name || "Лига"}
                </h2>
                <p className="text-gray-600">
                  Орын: <span className="font-bold text-xl">#{userLeagueInfo.rank || "?"}</span>
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-600">Апталық ұпай</p>
                <p className="text-4xl font-bold text-blue-600">⚡{userLeagueInfo.weekly_points}</p>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-300">
              <p className="text-sm text-gray-600">
                💡 Топ 3 жоғары лигаға көтеріледі • Соңғы 3 төмен лигаға түседі
              </p>
            </div>
          </div>
        )}

        {/* League Selector */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">
            🏆 Лигалар
          </h1>
          
          <div className="flex flex-wrap gap-3 justify-center">
            {leagues.map((league) => (
              <button
                key={league.id}
                onClick={() => setCurrentLeague(league.id)}
                className={`px-6 py-3 rounded-lg font-bold transition ${
                  currentLeague === league.id
                    ? "bg-blue-600 text-white shadow-lg scale-105"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {league.name}
              </button>
            ))}
          </div>
        </div>

        {/* League Leaderboard */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
            {leagues.find(l => l.id === currentLeague)?.name || "Лига"} - Апталық рейтинг
          </h2>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
              <p className="text-xl text-gray-600">Рейтинг жүктелуде...</p>
            </div>
          ) : leagueUsers.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-xl text-gray-600">Әзірше қолданушылар жоқ</p>
            </div>
          ) : (
            <div className="space-y-2">
              {leagueUsers.map((user, index) => {
                const position = index + 1;
                const zone = getPromotionZone(position, leagueUsers.length);
                const isCurrentUser = session?.user?.email && user.email === session.user.email;
                
                let displayName = '';
                if (user.source === 'telegram') {
                  displayName = user.username || user.full_name || `User ${user.user_id}`;
                } else {
                  displayName = user.nickname || user.name || 'Web User';
                }
                
                if (isCurrentUser) {
                  displayName += " (Сіз)";
                }
                
                return (
                  <div
                    key={user.source === 'telegram' ? `tg-${user.user_id}` : `web-${user.email}`}
                    className={`flex items-center justify-between p-4 rounded-lg transition ${
                      zone === "promotion"
                        ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-400'
                        : zone === "demotion"
                        ? 'bg-gradient-to-r from-red-50 to-pink-50 border-2 border-red-300'
                        : isCurrentUser
                        ? 'bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-400'
                        : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center gap-4 flex-1">
                      <span className={`text-2xl font-bold min-w-[50px] ${
                        zone === "promotion" ? 'text-green-600' : 
                        zone === "demotion" ? 'text-red-600' : 'text-gray-600'
                      }`}>
                        {position === 1 ? "👑" : `${position}.`}
                        {zone === "promotion" && " ⬆️"}
                        {zone === "demotion" && " ⬇️"}
                      </span>
                      <div className="flex-1">
                        <p className={`font-bold ${isCurrentUser ? 'text-lg text-blue-700' : 'text-base text-gray-800'}`}>
                          {displayName}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-blue-600">⚡{user.weekly_points}</p>
                      <p className="text-sm text-gray-500">💎 {user.points}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm text-gray-700">
              <strong>Ескерту:</strong> Апталық рейтинг жексенбі сайын нөлге тасталады. 
              Топ 3 қолданушы жоғары лигаға көтеріледі, соңғы 3 төмен лигаға түседі.
            </p>
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
