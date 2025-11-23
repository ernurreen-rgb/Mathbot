// web/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { cookies } from "next/headers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "EsepBot – Қазақстандық математика платформасы",
  description: "Олимпиадалық есептер, рейтинг, шешімдер және ұпай жинау",
};

// Кірген қолданушыны алу (сервер компоненті болғандықтан cookies() қолданамыз)
async function getCurrentUser() {
  const cookieStore = cookies();
  const userId = cookieStore.get("user_id")?.value;
  const userName = cookieStore.get("user_name")?.value;

  if (userId) {
    return {
      id: userId,
      name: userName || "Қолданушы",
    };
  }
  return null;
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getCurrentUser();

  return (
    <html lang="kk">
      <body className={`${inter.className} min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50`}>
        {/* Кірген қолданушыны көрсету */}
        {user && (
          <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white py-3 px-6 text-center font-bold shadow-lg">
            Сәлем, {user.name}! (ID: {user.id})
            <span className="ml-4 text-sm opacity-90">✅ Сіз жүйеге кірдіңіз</span>
          </div>
        )}

        {/* Негізгі контент */}
        <main className="flex flex-col items-center justify-center min-h-screen px-4">
          {children}
        </main>

        {/* Төменгі колонтитул (қаласаңыз кейін толықтырамыз) */}
        <footer className="absolute bottom-4 text-center text-gray-500 text-sm">
          © 2025 EsepBot – Қазақстандық олимпиадалық математика платформасы
        </footer>
      </body>
    </html>
  );
}