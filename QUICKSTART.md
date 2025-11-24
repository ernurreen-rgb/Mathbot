# 🚀 Quick Start - Deploy to Render in 5 Minutes

## Prerequisites
- GitHub account
- Render.com account (free) - [Sign up here](https://render.com)
- Telegram Bot Token from [@BotFather](https://t.me/botfather)

## Step 1: Get Telegram Bot Token (2 minutes)

1. Open Telegram and find [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Follow the instructions (choose name and username)
4. **Copy the token** - looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
5. Keep this token safe - you'll need it in Step 3

## Step 2: Deploy to Render (2 minutes)

1. **Fork this repository** to your GitHub account
   - Click "Fork" button at the top of this page

2. **Go to Render Dashboard**: https://dashboard.render.com/

3. **Create Blueprint**:
   - Click **"New"** → **"Blueprint"**
   - Connect your GitHub account (if not connected)
   - Select your forked repository
   - Render will detect `render.yaml` automatically
   - Click **"Apply"**

## Step 3: Configure Environment Variables (1 minute)

Render will create two services. You need to add environment variables:

### For `mathbot-api` service:

1. Go to the service in Render Dashboard
2. Click **"Environment"** tab
3. Add variable:
   - **Key**: `BOT_TOKEN`
   - **Value**: Your token from Step 1
4. Click **"Save Changes"**

### For `mathbot-web` service:

1. Go to the service in Render Dashboard
2. Click **"Environment"** tab
3. Add variables:
   - **Key**: `NEXTAUTH_URL`
   - **Value**: Your web service URL (e.g., `https://mathbot-web.onrender.com`)
   
   - **Key**: `NEXTAUTH_SECRET`
   - **Value**: Generate with: `openssl rand -base64 32` or use any random string

4. Click **"Save Changes"**

## Step 4: Wait for Deployment

- Both services will automatically build and deploy (takes 3-5 minutes)
- Watch the logs in Render Dashboard
- When you see "Live" badge - it's ready! 🎉

## Step 5: Test Your Bot

1. **Find your bot** on Telegram (the username you chose in Step 1)
2. Send `/start` to your bot
3. Try `/task` to get a math problem

## Step 6: Test Web App

1. Open your web service URL (shown in Render Dashboard)
2. Click "Get Random Task"
3. Solve a problem!

## URLs

After deployment, you'll have:
- **API/Bot**: `https://mathbot-api.onrender.com`
- **Web App**: `https://mathbot-web.onrender.com`

## Important Notes

### Free Tier
- Services sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- 750 free hours/month per service

### Adding Tasks
Use your Telegram bot to add tasks:
1. Send `/addtask` to your bot
2. Follow the instructions to upload problem images

## Troubleshooting

**Bot not responding?**
- Check that BOT_TOKEN is set correctly in Render Dashboard
- Check service logs for errors

**Web app can't connect to API?**
- Verify NEXT_PUBLIC_API_URL is correct in render.yaml
- Make sure both services are running (not sleeping)

**Need help?**
- See detailed guide: [DEPLOYMENT.md](./DEPLOYMENT.md) (English)
- См. подробную инструкцию: [DEPLOYMENT_RU.md](./DEPLOYMENT_RU.md) (Russian)

## Next Steps

1. ✅ Add math problems using `/addtask` in Telegram
2. ✅ Share your bot with friends
3. ✅ Customize the project
4. ✅ Upgrade to paid plan for 24/7 uptime (optional)

---

**That's it! You're done!** 🎉

Your math bot is now live and ready to use!
