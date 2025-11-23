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

  useEffect(() => {
    // Note: This would need an API endpoint in the bot
    // For now, showing a placeholder
    setLoading(false);
  }, []);

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center">
            🏆 Рейтинг
          </h1>

          <div className="text-center py-12">
            <div className="text-6xl mb-4">📊</div>
            <h2 className="text-2xl font-bold text-gray-800 mb-3">
              Рейтинг Telegram ботында
            </h2>
            <p className="text-gray-600 mb-6">
              Үздік қолданушыларды көру үшін Telegram ботына кіріп <span className="font-mono bg-gray-100 px-2 py-1 rounded">/rating</span> командасын енгізіңіз
            </p>
            <a
              href="https://t.me/yeramathbot"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-3 px-8 rounded-lg transition shadow-lg"
            >
              Telegram ботын ашу →
            </a>
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
