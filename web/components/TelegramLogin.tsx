// web/components/TelegramLogin.tsx

"use client";

import { useEffect } from "react";

export default function TelegramLogin() {
  useEffect(() => {
    // 1. Telegram Login Widget-тің JavaScript Callback функциясын анықтау
    // Бұл функция Widget арқылы кіру сәтті аяқталғанда іске қосылады.
    // @ts-ignore
    window.onTelegramAuth = async (user: any) => {
      // 2. Пайдаланушы деректерін /login/telegram API маршрутына жіберу
      const res = await fetch("/login/telegram", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user),
      });
      
      if (res.ok) {
        // 3. Егер API сәтті жауап берсе (cookie орнатылса), бетті жаңарту
        location.reload();
      } else {
        // 4. Қате болса (мысалы, 401 Unauthorized - Хэш тексеру қатесі)
        console.error("Authentication failed on server:", res.status);
        alert("Кіру сәтсіз аяқталды. Серверлік қатені тексеріңіз.");
      }
    };

    // 5. Telegram Widget скриптін жасау және атрибуттарды орнату
    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.async = true;
    
    script.setAttribute("data-telegram-login", "yeramathbot");
    script.setAttribute("data-size", "large");
    script.setAttribute("data-radius", "12");
    
    // 🛑 МІНЕ МӘСЕЛЕНІҢ ШЕШІМІ: data-auth-url-ді data-onauth-қа ауыстыру!
    script.setAttribute("data-onauth", "onTelegramAuth"); 
    
    // data-auth-url атрибуты ЖОЙЫЛДЫ
    
    script.setAttribute("data-request-access", "write");

    // 6. Скриптті DOM-ға қосу
    document.getElementById("tg-login")?.appendChild(script);
    
    // Cleanup function: Компонент жойылғанда onTelegramAuth-ты өшіру
    return () => {
        // @ts-ignore
        delete window.onTelegramAuth;
    };
    
  }, []);

  // Widget-ті енгізу үшін орын (контейнер)
  return <div id="tg-login" className="flex justify-center my-8" />;
}