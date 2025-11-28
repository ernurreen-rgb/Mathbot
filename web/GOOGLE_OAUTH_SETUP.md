# Google OAuth Setup Guide / Google OAuth орнату нұсқаулығы

This guide explains how to set up Google OAuth for the EsepBot web platform.

## Prerequisites / Алдын ала талаптар

- A Google account / Google аккаунты
- Access to Google Cloud Console / Google Cloud Console-ге қол жетімділік

## Step-by-Step Setup / Қадам бойынша орнату

### 1. Create a Google Cloud Project / Google Cloud жобасын құру

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top
3. Click "New Project"
4. Enter project name (e.g., "EsepBot")
5. Click "Create"

### 2. Enable Google+ API / Google+ API-ды іске қосу

1. Go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click "Enable"

### 3. Configure OAuth Consent Screen / OAuth келісім экранын конфигурациялау

1. Go to "APIs & Services" → "OAuth consent screen"
2. Select "External" (unless you have Google Workspace)
3. Click "Create"
4. Fill in the required information:
   - App name: EsepBot
   - User support email: your email
   - Developer contact email: your email
5. Click "Save and Continue"
6. Add scopes: `email`, `profile`, `openid`
7. Click "Save and Continue"
8. Add test users (your email) during development
9. Click "Save and Continue"

### 4. Create OAuth Credentials / OAuth тіркелгі деректерін жасау

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Web application"
4. Enter a name (e.g., "EsepBot Web Client")
5. Add **Authorized JavaScript origins**:
   - For development: `http://localhost:3000`
   - For production: `https://yourdomain.com`
6. Add **Authorized redirect URIs**:
   - For development: `http://localhost:3000/api/auth/callback/google`
   - For production: `https://yourdomain.com/api/auth/callback/google`
7. Click "Create"
8. Copy the **Client ID** and **Client Secret**

### 5. Configure Environment Variables / Қоршаған орта айнымалыларын конфигурациялау

Create a `.env.local` file in the `web` directory:

```bash
# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<generate with: openssl rand -base64 32>

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

### 6. Generate NEXTAUTH_SECRET / NEXTAUTH_SECRET генерациялау

Run this command to generate a secure secret:

```bash
openssl rand -base64 32
```

## Production Setup / Өндірістік орнату

For production deployment:

1. Update OAuth consent screen to "Production" mode (requires Google verification for public apps)
2. Add your production domain to authorized origins and redirect URIs
3. Update environment variables:

```bash
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXTAUTH_URL=https://your-web-domain.com
NEXTAUTH_SECRET=<your-production-secret>
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

## Troubleshooting / Мәселелерді шешу

### "Access blocked" error
- Make sure your email is added as a test user during development
- Check that redirect URIs exactly match (including trailing slashes)

### "Invalid redirect URI" error
- Verify the redirect URI in Google Console matches exactly:
  - Development: `http://localhost:3000/api/auth/callback/google`
  - Production: `https://yourdomain.com/api/auth/callback/google`

### NEXTAUTH_SECRET not set
- Generate a secret using: `openssl rand -base64 32`
- Add it to your `.env.local` file

## Security Best Practices / Қауіпсіздік бойынша ең жақсы тәжірибелер

1. Never commit secrets to git
2. Use environment variables for all sensitive data
3. Rotate secrets periodically
4. Use HTTPS in production
5. Keep OAuth consent screen information accurate and up-to-date
