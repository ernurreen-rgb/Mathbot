// web/components/TelegramLogin.tsx

"use client";

import { useEffect } from "react";

export default function TelegramLogin() {
  useEffect(() => {
    // Define the callback function globally before the widget script loads
    // @ts-ignore
    window.onTelegramAuth = async (user: any) => {
      console.log('[Telegram Auth] Received user data:', user);
      try {
        console.log('[Telegram Auth] Sending request to /login/telegram');
        const res = await fetch("/login/telegram", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(user),
        });
        const text = await res.text();
        console.log('[Telegram Auth] Server response:', res.status, text);
        if (res.ok) {
          console.log('[Telegram Auth] Login successful, reloading page');
          location.reload();
        } else {
          console.error('[Telegram Auth] Login failed:', res.status, text);
          alert("Кіру сәтсіз аяқталды. Серверлік қатені тексеріңіз. Код: " + res.status + "\n" + text);
        }
      } catch (e) {
        console.error('[Telegram Auth] Fetch error:', e);
        alert("Fetch error: " + (e as Error).message);
      }
    };

    console.log('[Telegram Widget] Initializing widget');
    
    // Create and configure the Telegram widget script
    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.async = true;
    script.setAttribute("data-telegram-login", "yeramathbot");
    script.setAttribute("data-size", "large");
    script.setAttribute("data-radius", "12");
    script.setAttribute("data-onauth", "onTelegramAuth(user)");
    script.setAttribute("data-request-access", "write");

    // Add error handler for script loading
    script.onerror = () => {
      console.error('[Telegram Widget] Failed to load widget script');
    };
    
    script.onload = () => {
      console.log('[Telegram Widget] Widget script loaded successfully');
    };

    // Append script to the container
    const container = document.getElementById("tg-login");
    if (container) {
      container.appendChild(script);
      console.log('[Telegram Widget] Widget script appended to DOM');
    } else {
      console.error('[Telegram Widget] Container element not found');
    }
    
    // Cleanup function
    return () => {
        console.log('[Telegram Widget] Cleaning up');
        // @ts-ignore
        delete window.onTelegramAuth;
        // Remove the script if it exists
        if (container && script.parentNode === container) {
          container.removeChild(script);
        }
    };
    
  }, []);

  return <div id="tg-login" className="flex justify-center my-8" />;
}
