# Google OAuth Setup Guide

## Google OAuth конфигурациясы

Google OAuth арқылы кіру мүмкіндігін қосу үшін келесі қадамдарды орындаңыз:

### 1. Google Cloud Console-де жоба құру

1. [Google Cloud Console](https://console.cloud.google.com/) сайтына кіріңіз
2. Жаңа жоба құрыңыз немесе бар жобаны таңдаңыз
3. "APIs & Services" > "Credentials" бөліміне өтіңіз

### 2. OAuth 2.0 Client ID құру

1. "Create Credentials" түймесін басыңыз
2. "OAuth client ID" таңдаңыз
3. Application type: "Web application"
4. Name: "EsepBot" (немесе қалаған атауыңыз)

### 3. Authorized redirect URIs қосу

Development үшін:
```
http://localhost:3000/api/auth/callback/google
```

Production үшін:
```
https://yourdomain.com/api/auth/callback/google
```

### 4. Credentials алу

Google сізге екі маңызды мән береді:
- **Client ID**: `123456789-abcdefg.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-abcdefghijklmnop`

### 5. Environment Variables орнату

`.env.local` файлын құрыңыз:

```bash
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-generated-secret-here

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

`NEXTAUTH_SECRET` генерациялау:
```bash
openssl rand -base64 32
```

### 6. Production орнату

Vercel/Netlify deployment кезінде Environment Variables қосыңыз:

```
NEXTAUTH_URL=https://yourdomain.com
NEXTAUTH_SECRET=your-generated-secret
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

## OAuth Consent Screen

Google Cloud Console-де "OAuth consent screen" конфигурациялаңыз:

1. User Type: "External" таңдаңыз
2. App name: "EsepBot"
3. User support email: сіздің email
4. Developer contact: сіздің email
5. Scopes: `email`, `profile` (автоматты қосылады)

## Тестілеу

1. Dependencies орнату:
```bash
cd web
npm install
```

2. Development server іске қосу:
```bash
npm run dev
```

3. Браузерде `http://localhost:3000` ашыңыз
4. "Google арқылы кіру" түймесін басыңыз
5. Google аккаунтыңызды таңдаңыз

## Қауіпсіздік ескертулері

- **NEXTAUTH_SECRET** құпия сөзін ешкімге көрсетпеңіз
- Production-да міндетті түрде HTTPS қолданыңыз
- `.env.local` файлын `.gitignore`-ға қосыңыз (автоматты қосылған)
- Әр environment үшін жеке `NEXTAUTH_SECRET` қолданыңыз

## Қосымша мәліметтер

- [NextAuth.js Documentation](https://next-auth.js.org/)
- [Google OAuth Guide](https://developers.google.com/identity/protocols/oauth2)
- [NextAuth Google Provider](https://next-auth.js.org/providers/google)
