# Deployment Guide

## Architecture
- **Frontend**: Vercel (React/Vite)
- **Backend**: Fly.io (FastAPI/Python)

## Prerequisites

### 1. Install CLI Tools

```bash
# Install Vercel CLI
npm install -g vercel

# Install Fly.io CLI (macOS)
brew install flyctl

# Or via curl (Linux/macOS)
curl -L https://fly.io/install.sh | sh
```

### 2. Create Accounts
- Vercel: https://vercel.com/signup
- Fly.io: https://fly.io/app/sign-up

### 3. Login to CLIs

```bash
# Login to Vercel
vercel login

# Login to Fly.io
flyctl auth login
```

## Backend Deployment (Fly.io)

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create Fly.io app
```bash
flyctl launch --no-deploy
# When prompted:
# - Choose app name: mobius-backend (or your preferred name)
# - Choose region: sea (Seattle) or closest to you
# - Don't deploy yet - we need to set secrets first
```

### 3. Set environment variables (secrets)
```bash
# Set all your API keys as secrets
flyctl secrets set \
  ANTHROPIC_API_KEY="your-anthropic-key" \
  ALPACA_API_KEY="your-alpaca-key" \
  ALPACA_SECRET_KEY="your-alpaca-secret" \
  JWT_SECRET_KEY="your-jwt-secret" \
  SUPABASE_URL="your-supabase-url" \
  SUPABASE_KEY="your-supabase-anon-key" \
  REDDIT_CLIENT_ID="your-reddit-id" \
  REDDIT_CLIENT_SECRET="your-reddit-secret" \
  REDDIT_USER_AGENT="your-app-name"
```

### 4. Deploy backend
```bash
flyctl deploy
```

### 5. Get your backend URL
```bash
flyctl info
# Look for "Hostname" - it will be something like: mobius-backend.fly.dev
```

### 6. Test backend
```bash
curl https://mobius-backend.fly.dev/health
# Should return: {"status":"healthy"}
```

## Frontend Deployment (Vercel)

### 1. Navigate to frontend directory
```bash
cd ../frontend/frontend
```

### 2. Create production environment file
```bash
# Create .env.production
echo "VITE_API_URL=https://mobius-backend.fly.dev" > .env.production
```

### 3. Deploy to Vercel
```bash
vercel

# First time:
# - Set up and deploy? Yes
# - Which scope? (choose your account)
# - Link to existing project? No
# - Project name? (accept default or choose)
# - Directory? (should auto-detect as ./)
# - Override settings? No

# Note: First deploy will be a preview URL
```

### 4. Deploy to production
```bash
vercel --prod
```

### 5. Get your frontend URL
```bash
# After deployment, you'll see:
# ✅ Production: https://your-app.vercel.app
```

## Backend CORS Update

After getting your Vercel URL, update backend CORS:

```bash
# Go back to backend directory
cd ../../backend
```

Edit `main.py` line ~25 to add your Vercel URL:

```python
origins = [
    "http://localhost:3000",
    "https://your-app.vercel.app",  # Add your Vercel URL here
]
```

Redeploy backend:
```bash
flyctl deploy
```

## Verification

1. **Test Backend Health**
   ```bash
   curl https://mobius-backend.fly.dev/health
   ```

2. **Test Frontend**
   - Open https://your-app.vercel.app in browser
   - Check browser console for API configuration logs
   - Try creating a strategy

3. **Test WebSocket**
   - Start a strategy generation
   - Watch for real-time agent activity logs
   - Should stream without "Connection closed unexpectedly" errors

## Environment Variables Summary

### Backend (Fly.io Secrets)
```bash
ANTHROPIC_API_KEY=sk-ant-...
ALPACA_API_KEY=PK...
ALPACA_SECRET_KEY=...
JWT_SECRET_KEY=your-secret-key
SUPABASE_URL=https://...supabase.co
SUPABASE_KEY=eyJ...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=YourApp/1.0
```

### Frontend (Vercel Environment Variables)
```bash
VITE_API_URL=https://mobius-backend.fly.dev
```

Set Vercel env vars via CLI:
```bash
vercel env add VITE_API_URL production
# Enter: https://mobius-backend.fly.dev
```

## Useful Commands

### Backend (Fly.io)
```bash
flyctl logs                  # View logs
flyctl status               # Check app status
flyctl scale memory 512     # Adjust memory
flyctl secrets list         # List secrets (values hidden)
flyctl ssh console          # SSH into container
```

### Frontend (Vercel)
```bash
vercel logs                 # View deployment logs
vercel list                 # List deployments
vercel env ls               # List environment variables
vercel rollback             # Rollback to previous deployment
```

## Costs

### Fly.io (Backend)
- **Free tier**: 3 shared-cpu VMs with 256MB RAM each
- **Your usage**: 1 VM with 512MB = ~$5/month
- **First $5/month free** with credit card

### Vercel (Frontend)
- **Free tier**:
  - 100GB bandwidth
  - Unlimited deployments
  - Custom domains
- **Your usage**: Well within free tier ✅

## Troubleshooting

### Backend won't start
```bash
flyctl logs
# Check for missing environment variables or import errors
```

### Frontend API calls failing
- Check CORS in backend main.py
- Verify VITE_API_URL in Vercel dashboard
- Check browser console for CORS errors

### WebSocket connection issues
- Ensure backend is using wss:// (automatically handled by Fly.io)
- Check firewall/network allows WebSocket connections
- Verify WebSocket URL in frontend config.js

### "Cannot find module" errors
- Ensure all dependencies in requirements.txt (backend)
- Ensure all dependencies in package.json (frontend)
- Try: `flyctl deploy --build-only` to test build

## Next Steps (Optional)

1. **Custom Domain**
   ```bash
   # Backend
   flyctl certs add yourdomain.com

   # Frontend
   vercel domains add yourdomain.com
   ```

2. **Database Scaling**
   - Current: Supabase free tier
   - Consider upgrading if >50k rows or >500MB

3. **Monitoring**
   - Fly.io: Built-in metrics at `flyctl dashboard`
   - Vercel: Analytics at vercel.com/dashboard

4. **CI/CD**
   - Both Vercel and Fly.io support GitHub auto-deploy
   - Just connect your repo in their dashboards
