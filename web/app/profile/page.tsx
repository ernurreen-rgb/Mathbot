// web/app/profile/page.tsx
"use client";

export default function ProfilePage() {
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
              Профильді көру үшін Telegram ботына кіріңіз
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
