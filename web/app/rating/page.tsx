// web/app/rating/page.tsx
"use client";

import { useState, useEffect } from "react";

interface User {
  user_id: number;
  username: string | null;
  full_name: string | null;
  points: number;
  solved_count: number;
}

export default function RatingPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetchRating();
  }, []);

  const fetchRating = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiUrl}/api/rating?limit=20`);
      if (!res.ok) {
        throw new Error("Рейтингті жүктеу мүмкін болмады");
      }
      const data = await res.json();
      setUsers(data.users || []);
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
          <p className="text-xl text-gray-600">Рейтинг жүктелуде...</p>
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
            onClick={fetchRating}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition"
          >
            Қайталап көру
          </button>
        </div>
      </div>
    );
  }

  const getMedalEmoji = (position: number) => {
    if (position === 1) return "🥇";
    if (position === 2) return "🥈";
    if (position === 3) return "🥉";
    return `${position}.`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center flex items-center justify-center gap-3">
            <span>🏆</span>
            <span>Рейтинг</span>
          </h1>

          {users.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-xl text-gray-600">Әзірше қолданушылар жоқ</p>
            </div>
          ) : (
            <div className="space-y-3">
              {users.map((user, index) => {
                const position = index + 1;
                const isTopThree = position <= 3;
                const displayName = user.username || user.full_name || `User ${user.user_id}`;
                
                return (
                  <div
                    key={user.user_id}
                    className={`flex items-center justify-between p-4 rounded-lg transition ${
                      isTopThree
                        ? 'bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-300 shadow-md'
                        : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center gap-4 flex-1">
                      <span className={`text-2xl font-bold ${isTopThree ? 'text-3xl' : 'text-gray-600'} min-w-[50px]`}>
                        {getMedalEmoji(position)}
                      </span>
                      <div className="flex-1">
                        <p className={`font-bold ${isTopThree ? 'text-lg' : 'text-base'} text-gray-800`}>
                          {displayName}
                        </p>
                        {user.username && user.full_name && (
                          <p className="text-sm text-gray-500">@{user.username}</p>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-blue-600">{user.points}</p>
                      <p className="text-sm text-gray-500">{user.solved_count} есеп</p>
                    </div>
                  </div>
                );
              })}
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
