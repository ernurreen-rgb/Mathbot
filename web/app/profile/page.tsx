// web/app/profile/page.tsx
"use client";

import { useState, useEffect, useCallback } from "react";

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

export default function ProfilePage() {
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchUserStats = useCallback(async () => {
    // Without Google auth, we can't fetch user-specific stats
    // Show a message to use Telegram bot instead
    setError(null);
    setLoading(false);
  }, [apiUrl]);

  useEffect(() => {
    fetchUserStats();
  }, [fetchUserStats]);

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
              Профильді көру үшін Telegram ботын қолданыңыз
            </h2>
            <p className="text-gray-600 mb-6">
              Қазіргі уақытта авторизация қосылмаған. Профильді көру және есеп шешу үшін Telegram ботын қолданыңыз.
            </p>
            <div className="space-y-4">
              <a
                href="https://t.me/yeramathbot"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-bold py-3 px-8 rounded-lg transition shadow-lg"
              >
                📱 Telegram ботын ашу
              </a>
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
