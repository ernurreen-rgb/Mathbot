// web/app/login/telegram/route.ts
import { NextRequest, NextResponse } from "next/server";
import crypto from "crypto";

// BOT_TOKEN-ді process.env арқылы оқимыз.
// Бұл Vercel-де орнатқан BOT_TOKEN мәнін қолдануды қамтамасыз етеді.
const BOT_TOKEN = process.env.BOT_TOKEN;

// Қауіпсіздікті қамтамасыз ету үшін токеннің бар-жоғын тексереміз
if (!BOT_TOKEN) {
  // Бұл тек серверде қате шығарғанда көрінеді, бірақ маңызды
  console.error("CRITICAL ERROR: BOT_TOKEN is not configured in Environment Variables.");
  // process.exit(1); // Қажет болса, серверді тоқтатуға болады
}

/**
 * Telegram-нан келген деректердің хэшін тексереді
 * @param data Telegram-нан келген барлық деректер, оның ішінде хэш
 * @param token Сіздің Telegram ботыңыздың құпия кілті
 * @returns Хэш дұрыс болса true, әйтпесе false
 */
function verifyTelegramAuth(data: Record<string, string>, token: string): boolean {
  const hash = data.hash;
  delete data.hash;
  
  // КІРІС ДЕРЕКТЕРІН СҰРЫПТАУ ЖӘНЕ ЖОЛҒА АЙНАЛДЫРУ
  const checkString = Object.keys(data)
    .sort()
    .map((k) => `${k}=${data[k]}`)
    .join("\n");
  
  // ҚҰПИЯ КІЛТТІ ГЕНЕРАЦИЯЛАУ (SHA256)
  const secret = crypto.createHash("sha256").update(token).digest();
  
  // HASHMAC ГЕНЕРАЦИЯЛАУ
  const hmac = crypto.createHmac("sha256", secret).update(checkString).digest("hex");
  
  // Салыстыру
  return hmac === hash;
}

export async function POST(req: NextRequest) {
  const body = await req.json();

  if (!BOT_TOKEN) {
    // Токен жоқ болса, 500 Internal Server Error қайтарамыз
    return new Response("Server error: Authentication token not configured", { status: 500 });
  }

  // 1. ХЭШТІ ТЕКСЕРУ
  if (!verifyTelegramAuth(body, BOT_TOKEN)) {
    // Егер хэш дұрыс болмаса
    return new Response("Unauthorized: Invalid data hash", { status: 401 });
  }

  // 2. АУТЕНТИФИКАЦИЯ ЖӘНЕ COOKIE ОРНАТУ
  
  // Пайдаланушы ID-ін сақтайтын cookie-ді орнатамыз.
  // HttpOnly: Клиенттік JS-тен оқуға болмайды (қауіпсіздік).
  // SameSite=Lax: CSRF-тен қорғайды.
  // Max-Age: 1 жылға орнатылады.

  const maxAge = 31536000; // 1 жыл секундпен

  // Next.js-те Cookie-ді орнату үшін NextResponse қолданған дұрыс
  const response = NextResponse.json({ status: "success", user_id: body.id }, { status: 200 });
  
  response.cookies.set("tg_user_id", body.id.toString(), {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production', // Тек HTTPS-те жұмыс істейді (Vercel)
    sameSite: 'lax',
    path: '/',
    maxAge: maxAge,
  });

  // Екінші cookie-ді сақтау (мысалы, тек көрсету үшін)
  response.cookies.set("tg_username", body.first_name || "User", {
    httpOnly: false, // Қажет болса, клиенттік JS-тен оқуға рұқсат
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    path: '/',
    maxAge: maxAge,
  });

  return response;
}