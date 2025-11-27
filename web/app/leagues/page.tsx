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
  league_group_id?: number;
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
      // Fallback leagues for UI display when API is unavailable
      setLeagues([
        { id: "bronze", name: "🥉 Қола" },
        { id: "silver", name: "🥈 Күміс" },
        { id: "gold", name: "🥇 Алтын" },
        { id: "platinum", name: "💎 Платина" },
        { id: "diamond", name: "👑 Алмас" }
      ]);
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
      // Егер қолданушының өз лигасы болса, оның тобын көрсету
      let url = `${apiUrl}/api/league/${league}?limit=30`;
      if (session?.user?.email && userLeagueInfo?.league === league && userLeagueInfo?.league_group_id) {
        url += `&group_id=${userLeagueInfo.league_group_id}`;
      }
      
      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(`Сервер қатесі: ${res.status}`);
      }
      const data = await res.json();
      setLeagueUsers(data.users || []);
    } catch (err) {
      console.error("Failed to fetch league leaderboard:", err);
      // Don't show global error, just show empty users
      setLeagueUsers([]);
    } finally {
      setLoading(false);
    }
  };

  // Error state
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-4">
        <div className="w-full max-w-md text-center p-6 bg-white rounded-2xl shadow-xl">
          <div className="text-4xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-red-600 mb-3">Қате</h2>
          <p className="text-gray-700 mb-6 text-sm break-words">{error}</p>
          <button
            onClick={() => fetchLeagueLeaderboard(currentLeague)}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-xl transition mb-3"
          >
            🔄 Қайталап көру
          </button>
          <a
            href="/"
            className="block text-blue-600 hover:text-blue-800 font-semibold"
          >
            ← Басты бетке қайту
          </a>
        </div>
      </div>
    );
  }

  // Helper functions
  
  // Removes the emoji prefix from league name (e.g., "🥉 Қола" -> "Қола")
  const getLeagueNameWithoutEmoji = (fullName: string | undefined): string => {
    if (!fullName) return "Лига";
    // Pattern matches: emoji (or any non-space chars) followed by a space at the start
    return fullName.replace(/^[^\s]+\s/, '') || fullName;
  };
  
  const getLeagueEmoji = (leagueId: string) => {
    const emojis: Record<string, string> = {
      bronze: "🥉",
      silver: "🥈",
      gold: "🥇",
      platinum: "💎",
      diamond: "👑"
    };
    return emojis[leagueId] || "🏆";
  };

  const getLeagueBgColor = (leagueId: string) => {
    const colors: Record<string, string> = {
      bronze: "bg-gradient-to-br from-orange-100 to-amber-50",
      silver: "bg-gradient-to-br from-gray-100 to-slate-50",
      gold: "bg-gradient-to-br from-yellow-100 to-amber-50",
      platinum: "bg-gradient-to-br from-cyan-100 to-blue-50",
      diamond: "bg-gradient-to-br from-purple-100 to-pink-50"
    };
    return colors[leagueId] || colors.bronze;
  };

  const getPromotionZone = (position: number, total: number) => {
    const PROMOTION_THRESHOLD = 7;
    const DEMOTION_THRESHOLD = 5;
    const MIN_USERS_FOR_DEMOTION = PROMOTION_THRESHOLD + DEMOTION_THRESHOLD + 1;
    
    if (position <= PROMOTION_THRESHOLD) return "promotion";
    if (position > total - DEMOTION_THRESHOLD && total >= MIN_USERS_FOR_DEMOTION) return "demotion";
    return "safe";
  };

  const getDisplayName = (user: User) => {
    if (user.source === 'telegram') {
      return user.username || user.full_name || `User ${user.user_id}`;
    }
    return user.nickname || user.name || 'Web User';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Main container with safe padding */}
      <div className="w-full max-w-lg mx-auto px-4 py-6 pb-20">
        
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">🏆 Лигалар</h1>
          <p className="text-sm text-gray-500 mt-1">Апталық жарыс</p>
        </div>

        {/* User's Current League Card */}
        {session && userLeagueInfo && (
          <div className={`${getLeagueBgColor(userLeagueInfo.league)} rounded-2xl p-4 mb-5 shadow-lg border border-white/50`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <span className="text-3xl">{getLeagueEmoji(userLeagueInfo.league)}</span>
                <div>
                  <p className="font-bold text-gray-800">
                    {getLeagueNameWithoutEmoji(leagues.find(l => l.id === userLeagueInfo.league)?.name)}
                  </p>
                  <p className="text-xs text-gray-600">
                    Орын: <span className="font-bold">#{userLeagueInfo.rank || "?"}</span>
                    {userLeagueInfo.league_group_id && (
                      <span className="ml-2">• Топ #{userLeagueInfo.league_group_id}</span>
                    )}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-blue-600">⚡{userLeagueInfo.weekly_points}</p>
                <p className="text-xs text-gray-500">апталық</p>
              </div>
            </div>
            
            {!userLeagueInfo.league_group_id && (
              <div className="bg-amber-100 text-amber-800 text-xs p-2 rounded-lg text-center">
                ⚠️ Топқа қосылу үшін есеп шешіңіз!
              </div>
            )}
          </div>
        )}

        {/* League Selector - Horizontal scroll */}
        <div className="mb-5">
          <div className="flex gap-2 overflow-x-auto whitespace-nowrap pb-2 scrollbar-hide">
            {leagues.map((league) => (
              <button
                key={league.id}
                onClick={() => setCurrentLeague(league.id)}
                className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-semibold transition-all ${
                  currentLeague === league.id
                    ? "bg-blue-600 text-white shadow-md"
                    : "bg-white text-gray-700 border border-gray-200"
                }`}
              >
                {league.name}
              </button>
            ))}
          </div>
        </div>

        {/* Leaderboard Card */}
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          {/* Leaderboard Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3">
            <h2 className="text-white font-bold text-center">
              {leagues.find(l => l.id === currentLeague)?.name || "Лига"} рейтингі
            </h2>
          </div>

          {/* Loading State */}
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="animate-spin rounded-full h-10 w-10 border-4 border-blue-200 border-t-blue-600 mb-3"></div>
              <p className="text-gray-500 text-sm">Жүктелуде...</p>
            </div>
          ) : leagueUsers.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <span className="text-4xl mb-3">🏜️</span>
              <p className="text-gray-500">Қолданушылар жоқ</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {leagueUsers.map((user, index) => {
                const position = index + 1;
                const zone = getPromotionZone(position, leagueUsers.length);
                const isCurrentUser = session?.user?.email && user.email === session.user.email;
                const displayName = getDisplayName(user);
                
                // Position indicator styling
                let positionBg = "bg-gray-100 text-gray-600";
                let rowBg = "";
                
                if (zone === "promotion") {
                  positionBg = "bg-green-500 text-white";
                  rowBg = "bg-green-50";
                } else if (zone === "demotion") {
                  positionBg = "bg-red-400 text-white";
                  rowBg = "bg-red-50";
                } else if (isCurrentUser) {
                  positionBg = "bg-blue-500 text-white";
                  rowBg = "bg-blue-50";
                }
                
                return (
                  <div
                    key={user.source === 'telegram' ? `tg-${user.user_id}` : `web-${user.email}`}
                    className={`flex items-center gap-3 px-4 py-3 ${rowBg}`}
                  >
                    {/* Position indicator with accessibility */}
                    <div 
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${positionBg}`}
                      aria-label={`Орын ${position}`}
                      role="text"
                    >
                      {position === 1 ? "👑" : position}
                    </div>
                    
                    {/* User info */}
                    <div className="flex-1 min-w-0">
                      <p className={`font-semibold truncate ${isCurrentUser ? 'text-blue-700' : 'text-gray-800'}`}>
                        {displayName}
                        {isCurrentUser && <span className="text-blue-500 ml-1">(Сіз)</span>}
                      </p>
                      <p className="text-xs text-gray-400">💎 {user.points} ұпай</p>
                    </div>
                    
                    {/* Weekly points */}
                    <div className="flex items-center gap-1 flex-shrink-0">
                      <span className="text-lg font-bold text-blue-600">⚡{user.weekly_points}</span>
                      {zone === "promotion" && <span className="text-green-500">↑</span>}
                      {zone === "demotion" && <span className="text-red-500">↓</span>}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Legend */}
          <div className="bg-gray-50 px-4 py-3 border-t border-gray-100">
            <div className="flex flex-wrap justify-center gap-3 text-xs">
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                <span className="text-gray-600">Көтеріледі (Топ 7)</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 bg-red-400 rounded-full"></span>
                <span className="text-gray-600">Түседі (Соңғы 5)</span>
              </span>
            </div>
          </div>
        </div>

        {/* Info note */}
        <div className="mt-4 p-3 bg-blue-50 rounded-xl border border-blue-100">
          <p className="text-xs text-gray-600 text-center">
            📅 Апталық рейтинг жексенбі сайын нөлге тасталады
          </p>
        </div>

        {/* Back button */}
        <div className="mt-6 text-center">
          <a
            href="/"
            className="inline-block text-blue-600 hover:text-blue-800 font-semibold text-sm"
          >
            ← Басты бетке қайту
          </a>
        </div>
      </div>
    </div>
  );
}
