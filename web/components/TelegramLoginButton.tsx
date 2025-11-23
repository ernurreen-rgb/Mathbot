"use client";
import { useEffect } from "react";

export default function TelegramLoginButton() {
  useEffect(() => {
    // @ts-ignore
    window.TelegramLogin = function() {
      const script = document.createElement("script");
      script.src = "https://telegram.org/js/telegram-widget.js?22";
      script.setAttribute("data-telegram-login", "yeramathbot"); // BotFather-дағы username
      script.setAttribute("data-size", "large");
      script.setAttribute("data-onauth", "onTelegramAuth(user)");
      script.setAttribute("data-request-access", "write");
      script.async = true;
      document.getElementById("telegram-login")?.appendChild(script);
    };

    // @ts-ignore
    window.onTelegramAuth = (user: any) => {
      fetch("/login/telegram/callback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user),
      }).then(() => location.reload());
    };

    window.TelegramLogin();
  }, []);

  return <div id="telegram-login" className="my-2" />;
}