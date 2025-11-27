// web/app/layout.tsx
import type { Metadata } from "next";
import "./globals.css";
import SessionProvider from "@/components/SessionProvider";
import UserBar from "@/components/UserBar";

export const metadata: Metadata = {
  title: "EsepBot – Қазақстандық математика платформасы",
  description: "Олимпиадалық есептер, рейтинг, шешімдер және ұпай жинау",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="kk">
      <body className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 font-sans">
        <SessionProvider>
          {/* Кірген қолданушыны көрсету */}
          <UserBar />

          {/* Негізгі контент */}
          <main className="w-full">
            {children}
          </main>

          {/* Төменгі колонтитул */}
          <footer className="absolute bottom-4 text-center text-gray-500 text-sm">
            © 2025 EsepBot – Қазақстандық олимпиадалық математика платформасы
          </footer>
        </SessionProvider>
      </body>
    </html>
  );
}