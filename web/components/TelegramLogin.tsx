"use client";

import { useEffect } from "react";

export default function TelegramLogin() {
  useEffect(() => {
    // ВЕРСИЯ 2: Өндірістік доменде жұмыс істейді (Vercel)
    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.async = true;
    script.setAttribute("data-telegram-login", "yeramathbot");
    script.setAttribute("data-size", "large");
    script.setAttribute("data-radius", "12");
    
    // ⚠️ МАҢЫЗДЫ: Бұл жерде сіздің Vercel доменіңіз тұруы керек!
    // Мысалы, егер домен esepbot.vercel.app болса:
    script.setAttribute("data-auth-url", "https://mathbot-nu.vercel.app/api/auth/telegram");
    
    script.setAttribute("data-request-access", "write");

    // data-test-server="true" ЖОЙЫЛДЫ, себебі енді нақты HTTPS доменіндеміз

    // @ts-ignore
    window.onTelegramAuth = async (user: any) => {
      // data-onauth callback арқылы fetch жасау
      const res = await fetch("/api/auth/telegram", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user),
      });
      
      if (res.ok) {
        location.reload();
      } else {
        // Егер fetch сәтсіз болса, бұл Telegram-ның хэш-верификациясының қатесі болуы мүмкін.
        alert("Аутентификация сәтсіз аяқталды. Токенді немесе хэшті тексеріңіз.");
      }
    };

    document.getElementById("tg-login")?.appendChild(script);
  }, []);

  return <div id="tg-login" className="flex justify-center my-8" />;
}