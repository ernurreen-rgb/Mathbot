// web/app/page.tsx
// import TelegramLogin from "@/components/TelegramLogin";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="text-center max-w-3xl">
        {/* Басты логотип */}
        <h1 className="text-7xl md:text-8xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-700 mb-6">
          EsepBot
        </h1>

        {/* Сипаттама */}
        <p className="text-2xl md:text-3xl text-gray-800 mb-4 font-medium">
          Қазақстандық олимпиадалық математика платформасы
        </p>

        <p className="text-lg md:text-xl text-gray-600 mb-12 leading-relaxed">
          Күнде жаңа есептер • Нағыз олимпиадалық есептер • Рейтинг • Шешімдер • Ұпай жинау
        </p>

        {/* Navigation buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
          <a
            href="/tasks"
            className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl transition shadow-lg transform hover:scale-105"
          >
            🧩 Есептер
          </a>
          <a
            href="/rating"
            className="w-full sm:w-auto bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-4 px-8 rounded-xl transition shadow-lg transform hover:scale-105"
          >
            🏆 Рейтинг
          </a>
          <a
            href="/profile"
            className="w-full sm:w-auto bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white font-bold py-4 px-8 rounded-xl transition shadow-lg transform hover:scale-105"
          >
            👤 Профиль
          </a>
        </div>

        {/* Telegram Login кнопкасы - temporarily hidden */}
        {/* <div className="flex flex-col items-center gap-8">
          <div className="bg-white p-6 rounded-3xl shadow-2xl border border-blue-100">
            <TelegramLogin />
          </div>

          <button className="text-blue-600 hover:text-blue-800 font-semibold text-lg underline decoration-2 underline-offset-4 transition">
            Қалай жұмыс істейді?
          </button>
        </div> */}

        {/* Төменгі статистика */}
        <div className="mt-20 text-gray-500 text-sm md:text-base">
          <p>
            Қазір {new Date().toLocaleDateString("kk-KZ", {
              day: "numeric",
              month: "long",
              year: "numeric"
            })}
          </p>
          <p className="mt-2">
            10 000+ шешілген есеп • 5 000+ белсенді оқушы
          </p>
        </div>
      </div>
    </div>
  );
}