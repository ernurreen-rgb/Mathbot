# Deployment Guide for Render

This guide explains how to deploy the Mathbot project to Render.com.

## Project Structure

This project consists of two services:
1. **Bot/API Service**: Python service running the Telegram bot and FastAPI backend
2. **Web Service**: Next.js frontend application

## Prerequisites

- A Render.com account (free tier works)
- A GitHub repository with this code
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))

## Deployment Steps

### Option 1: Using render.yaml (Recommended)

1. **Fork or push this repository to GitHub**

2. **Go to Render Dashboard** (https://dashboard.render.com/)

3. **Create New Blueprint Instance**
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file
   - Click "Apply"

4. **Configure Environment Variables**
   
   For **mathbot-api** service, add:
   ```
   BOT_TOKEN=your_telegram_bot_token_here
   PORT=8000
   ```

   For **mathbot-web** service, add:
   ```
   NEXT_PUBLIC_API_URL=https://mathbot-api.onrender.com
   NEXTAUTH_URL=https://mathbot-web.onrender.com
   NEXTAUTH_SECRET=<generate with: openssl rand -base64 32>
   ```

   Optional (for Google OAuth):
   ```
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   ```

5. **Deploy**
   - Render will build and deploy both services automatically
   - The API service will be available at: `https://mathbot-api.onrender.com`
   - The Web service will be available at: `https://mathbot-web.onrender.com`

### Option 2: Manual Deployment

#### Deploy Bot/API Service

1. **Create New Web Service**
   - Go to Render Dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: mathbot-api
     - **Environment**: Python 3
     - **Region**: Frankfurt (or closest to you)
     - **Branch**: main
     - **Root Directory**: bot
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python main.py`
     - **Plan**: Free

2. **Add Environment Variables**:
   ```
   BOT_TOKEN=your_telegram_bot_token_here
   PYTHON_VERSION=3.11.0
   ```

#### Deploy Web Service

1. **Create New Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: mathbot-web
     - **Environment**: Node
     - **Region**: Frankfurt
     - **Branch**: main
     - **Root Directory**: web
     - **Build Command**: `npm install && npm run build`
     - **Start Command**: `npm start`
     - **Plan**: Free

2. **Add Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://mathbot-api.onrender.com
   NEXTAUTH_URL=https://mathbot-web.onrender.com
   NEXTAUTH_SECRET=<your-secret-here>
   NODE_VERSION=18.17.0
   ```

## ⚠️ IMPORTANT: Why Tasks Disappear on Redeploy?

### The Problem

Every time you deploy (push code to main branch) on Render, **all data is lost**:
- SQLite database (`database.db`) — **deleted**
- Task images (`bot/images/`, `bot/solutions/`) — **deleted**

This happens because Render uses **ephemeral (temporary) storage** on the free tier. Each deploy creates a new container with a clean filesystem.

### Solutions

#### Option 1: Render Disk (Recommended for simplicity)

Render Disk is persistent storage that survives deploys.

1. **Go to mathbot-api service settings** in Render dashboard
2. **Add a Disk**:
   - Click "Add Disk"
   - **Name**: mathbot-data
   - **Mount Path**: `/data`
   - **Size**: 1 GB (enough to start)
3. **Add environment variables**:
   ```
   DATABASE_PATH=/data/database.db
   IMAGES_PATH=/data/images
   SOLUTIONS_PATH=/data/solutions
   ```

**Note**: Render Disk is only available on paid plans (from $7/month).

#### Option 2: External PostgreSQL Database

1. **Create PostgreSQL on Render**:
   - Click "New" → "PostgreSQL"
   - Choose free tier (90 days) or paid
2. **Get DATABASE_URL** from database settings
3. **Add environment variable** to mathbot-api:
   ```
   DATABASE_URL=postgres://user:password@host:port/database
   ```

**Note**: Code modification needed to support PostgreSQL.

#### Option 3: Use Different Hosting

Consider hosts with persistent storage:
- **Railway.app** — has persistent storage
- **Fly.io** — supports persistent volumes
- **DigitalOcean App Platform** — with managed databases
- **Your own VPS** (DigitalOcean, Hetzner, etc.)

#### Option 4: Manual Backup Before Deploy

If you continue using Render free tier:

1. **Before each deploy** export data:
   - In Telegram bot: `/export` — exports users
   - Download images manually via SSH/SFTP
   
2. **After deploy** import data back

**This is a temporary workaround and NOT recommended for production!**

### Recommendation

For stable bot operation with data persistence:

| Component | Free Solution | Paid Solution |
|-----------|---------------|---------------|
| Database | PostgreSQL (Render, 90 days free) | Render PostgreSQL ($7+/mo) |
| Images | Cloudinary (free tier) | AWS S3, Cloudinary Pro |
| Hosting | Render Free | Render Starter ($7/mo) |

---

## Important Notes

### Free Tier Limitations
- Services on the free tier will spin down after 15 minutes of inactivity
- First request after inactivity may take 30-60 seconds to wake up
- Free tier includes 750 hours/month per service
- **Data is NOT preserved between deploys!**

### Database Persistence
- The SQLite database (`database.db`) is stored on ephemeral disk
- **⚠️ Database is reset on every deploy!**
- For production, you **must** use an external database service

### Images Storage
- Images are stored in `bot/images/` and `bot/solutions/` directories
- **⚠️ Images are deleted on every deploy!**
- For production, you **must** use cloud storage (S3, Cloudinary, etc.)

### Custom Domain
- You can add a custom domain in the Render dashboard
- Update `NEXTAUTH_URL` and `NEXT_PUBLIC_API_URL` accordingly

## Testing Deployment

1. **Test API Service**:
   ```bash
   curl https://mathbot-api.onrender.com/api/rating
   ```

2. **Test Web Service**:
   - Visit `https://mathbot-web.onrender.com` in your browser
   - Try solving a random task

3. **Test Telegram Bot**:
   - Send `/start` to your bot on Telegram
   - Try the `/task` command

## Troubleshooting

### Bot API not responding
- Check that `BOT_TOKEN` is set correctly
- Check logs in Render Dashboard
- Verify that the service is running (not sleeping)

### Web can't connect to API
- Verify `NEXT_PUBLIC_API_URL` points to the correct API service URL
- Check CORS settings if needed
- Check both services are running

### Database errors
- Check if database was initialized properly
- Review logs for SQL errors
- Ensure `database.db` has correct permissions

## Updating Your Deployment

Render automatically deploys when you push to your GitHub repository:
```bash
git add .
git commit -m "Update feature"
git push
```

## Production Recommendations

For a production deployment, consider:

1. **Upgrade from Free Tier** for:
   - No spin-down on inactivity
   - More resources
   - Better performance

2. **Use External Database**:
   - PostgreSQL on Render
   - Or other managed database service

3. **Use Cloud Storage**:
   - AWS S3
   - Cloudinary
   - Google Cloud Storage

4. **Set up monitoring**:
   - Error tracking (Sentry)
   - Uptime monitoring
   - Performance monitoring

5. **Configure proper secrets management**
   - Never commit secrets to Git
   - Use Render's environment variables
   - Rotate secrets regularly

## Support

For Render-specific issues, check:
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com/)
