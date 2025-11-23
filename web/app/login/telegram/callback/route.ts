// web/app/api/auth/telegram/route.ts
import { NextRequest } from "next/server";
import crypto from "crypto";

const BOT_TOKEN = "8291254406:AAEsjXgHrTo5uv8_37dDyAgitx2ze1LNlx8"; // ← СІЗДІҢ ТОКЕНІҢІЗ

function verifyTelegramAuth(data: Record<string, string>): boolean {
  const hash = data.hash;
  delete data.hash;
  const checkString = Object.keys(data)
    .sort()
    .map((k) => `${k}=${data[k]}`)
    .join("\n");
  const secret = crypto.createHash("sha256").update(BOT_TOKEN).digest();
  const hmac = crypto.createHmac("sha256", secret).update(checkString).digest("hex");
  return hmac === hash;
}

export async function POST(req: NextRequest) {
  const body = await req.json();

  if (!verifyTelegramAuth(body)) {
    return new Response("Unauthorized", { status: 401 });
  }

  // Сессияны cookie-мен сақтаймыз
  const headers = new Headers();
  headers.append(
    "Set-Cookie",
    `user_id=${body.id};user_name=${body.first_name || ""}; Path=/; HttpOnly; SameSite=Lax; Max-Age=31536000`
  );

  return new Response("OK", { status: 200, headers });
}