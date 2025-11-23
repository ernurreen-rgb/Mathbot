// web/components/UserBar.tsx
"use client";

import { useSession, signOut } from "next-auth/react";

export default function UserBar() {
  const { data: session } = useSession();

  if (!session?.user) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white py-3 px-6 flex items-center justify-between shadow-lg">
      <div className="flex items-center gap-4">
        {session.user.image && (
          <img
            src={session.user.image}
            alt={session.user.name || "User"}
            className="w-10 h-10 rounded-full border-2 border-white"
          />
        )}
        <div>
          <div className="font-bold">
            Сәлем, {session.user.name || "Қолданушы"}!
          </div>
          <div className="text-sm opacity-90">
            {session.user.email}
          </div>
        </div>
      </div>
      <button
        onClick={() => signOut({ callbackUrl: "/" })}
        className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg transition font-semibold"
      >
        Шығу
      </button>
    </div>
  );
}
