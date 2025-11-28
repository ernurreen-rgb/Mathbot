// web/app/page.tsx
"use client";

import { useSession, signIn, signOut } from "next-auth/react";

export default function Home() {
  const { data: session, status } = useSession();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="text-center max-w-3xl">
        {/* Auth status */}
        <div className="absolute top-4 right-4">
          {status === "loading" ? (
            <div className="text-gray-500 text-sm">Жүктелуде...</div>
          ) : session ? (
            <div className="flex items-center gap-3 bg-white rounded-lg shadow-md px-4 py-2">
              {session.user?.image && (
                <img
                  src={session.user.image}
                  alt="Profile"
                  className="w-8 h-8 rounded-full"
                />
              )}
              <span className="text-gray-700 text-sm font-medium">
                {session.user?.name}
              </span>
              <button
                onClick={() => signOut()}
                className="text-red-600 hover:text-red-800 text-sm font-semibold"
              >
                Шығу
              </button>
            </div>
          ) : (
            <button
              onClick={() => signIn("google")}
              className="flex items-center gap-2 bg-white border border-gray-200 hover:border-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-lg transition shadow-md"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
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
              Кіру
            </button>
          )}
        </div>

        {/* Басты логотип */}
        <h1 className="text-7xl md:text-8xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-700 mb-6">
          EsepBot
        </h1>

        {/* Сипаттама */}
        <p className="text-2xl md:text-3xl text-gray-800 mb-4 font-medium">
          Ернұр ағайдың есептері
        </p>
        
        {/* Сипаттама 
        <p className="text-lg md:text-xl text-gray-600 mb-12 leading-relaxed">
          Күнде жаңа есептер • Лигалық жүйе • Апталық жарыстар
        </p>*/}

        {/* Navigation buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
          <a
            href="/tasks"
            className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl transition shadow-lg transform hover:scale-105"
          >
            🧩 Есептер
          </a>
          <a
            href="/leagues"
            className="w-full sm:w-auto bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white font-bold py-4 px-8 rounded-xl transition shadow-lg transform hover:scale-105"
          >
            🏆 Лигалар
          </a>
          <a
            href="/rating"
            className="w-full sm:w-auto bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-4 px-8 rounded-xl transition shadow-lg transform hover:scale-105"
          >
            📊 Рейтинг
          </a>
          <a
            href="/profile"
            className="w-full sm:w-auto bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white font-bold py-4 px-8 rounded-xl transition shadow-lg transform hover:scale-105"
          >
            👤 Профиль
          </a>
        </div>

        {/* Admin link - only visible for admins */}
        {session && (
          <div className="mt-4">
            <a
              href="/admin"
              className="text-gray-500 hover:text-gray-700 text-sm font-medium underline"
            >
              🔧 Әкімші панелі
            </a>
          </div>
        )}
      </div>
    </div>
  );
}