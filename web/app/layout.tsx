// web/app/layout.tsx
import type { Metadata } from "next";
import "./globals.css";
import Providers from "@/components/Providers";

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
        <Providers>
          {/* Негізгі контент */}
          <main className="flex flex-col items-center justify-center min-h-screen px-4">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}