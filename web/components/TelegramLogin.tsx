"use client";

import { useEffect } from "react";

export default function TelegramLogin() {
  useEffect(() => {
    // TEST MODE + localhost рұқсат ету
    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.async = true;
    script.setAttribute("data-telegram-login", "yeramathbot");
    script.setAttribute("data-size", "large");
    script.setAttribute("data-radius", "12");
    script.setAttribute("data-onauth", "onTelegramAuth(user)");
    script.setAttribute("data-request-access", "write");

    // ЕҢ МАҢЫЗДЫСЫ – осы екі жол localhost-та жұмыс істетеді!
    script.setAttribute("data-test-server", "true");

    // @ts-ignore
    window.onTelegramAuth = async (user: any) => {
      const res = await fetch("/api/auth/telegram", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user),
      });
      if (res.ok) {
        location.reload();
      } else {
        alert("Қате болды, бірақ бәрі жақсы – қайта басыңыз");
      }
    };

    document.getElementById("tg-login")?.appendChild(script);
  }, []);

  return <div id="tg-login" className="flex justify-center my-8" />;
}