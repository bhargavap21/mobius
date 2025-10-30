# Deployment Setup - Action Items

## ✅ Completed

1. **Created deployment configuration files:**
   - `backend/Dockerfile` - Container configuration for Fly.io
   - `backend/fly.toml` - Fly.io app configuration
   - `backend/.dockerignore` - Docker build optimization
   - `frontend/frontend/vercel.json` - Vercel deployment settings
   - `frontend/frontend/.env.example` - Environment variable template
   - `frontend/frontend/src/config.js` - API URL configuration

2. **Created documentation:**
   - `DEPLOYMENT_GUIDE.md` - Complete step-by-step deployment instructions
   - This file - Setup checklist

## 🔧 TODO: Update Frontend Code

The frontend currently has hardcoded `http://localhost:8000` URLs. These need to be replaced with the config import.

### Files that need updating:

Each file below needs two changes:
1. Add import at the top: `import { API_URL, WS_URL } from './config'` (adjust path as needed)
2. Replace `'http://localhost:8000'` with `\`\${API_URL}\``
3. Replace `'ws://localhost:8000'` with `\`\${WS_URL}\``

**List of files:**
- `frontend/frontend/src/App.jsx` (10 occurrences)
- `frontend/frontend/src/main.jsx` (1 occurrence)
- `frontend/frontend/src/context/AuthContext.jsx` (3 occurrences)
- `frontend/frontend/src/components/EmailConfirmation.jsx` (1 occurrence)
- `frontend/frontend/src/components/StrategySidebar.jsx` (1 occurrence)
- `frontend/frontend/src/components/BotLibrary.jsx` (4 occurrences)
- `frontend/frontend/src/components/ChatHistorySidebar.jsx` (3 occurrences)
- `frontend/frontend/src/components/DeploymentMonitor.jsx` (6 occurrences)
- `frontend/frontend/src/components/DeploymentPage.jsx` (1 occurrence)
- `frontend/frontend/src/components/AgentActivityLogWS.jsx` (1 occurrence - WebSocket)
- `frontend/frontend/src/pages/CommunityPage.jsx` (6 occurrences)

### Example Change:

**Before:**
```javascript
const response = await fetch('http://localhost:8000/api/sessions', {
```

**After:**
```javascript
import { API_URL } from '../config'  // Add at top of file

// ... later in code:
const response = await fetch(`${API_URL}/api/sessions`, {
```

**For WebSocket:**
```javascript
import { WS_URL } from '../config'

const wsUrl = `${WS_URL}/ws/strategy/progress/${sessionId}`
```

## 📝 Manual Steps Before Deployment

1. **Update all frontend files** with config imports (listed above)

2. **Test locally:**
   ```bash
   # Terminal 1: Start backend
   cd backend
   uvicorn main:app --reload

   # Terminal 2: Start frontend
   cd frontend/frontend
   npm run dev

   # Verify everything still works
   ```

3. **Update backend CORS** after you get Vercel URL:
   - Edit `backend/main.py` line ~25
   - Add your production Vercel URL to `origins` list

## 🚀 Ready to Deploy?

Once frontend code is updated:

1. **Install CLIs:**
   ```bash
   npm install -g vercel
   brew install flyctl  # or: curl -L https://fly.io/install.sh | sh
   ```

2. **Follow the complete guide:**
   - See `DEPLOYMENT_GUIDE.md` for detailed step-by-step instructions

## Estimated Time

- Frontend code updates: **15-20 minutes** (manual find-replace in each file)
- Backend deployment (Fly.io): **10 minutes**
- Frontend deployment (Vercel): **5 minutes**
- Testing & verification: **10 minutes**

**Total:** ~45 minutes

## Alternative: Quick Script

I created `update-api-urls.sh` that does a bulk find-replace, but you'll still need to:
1. Add the imports manually to each file
2. Verify the replacements are correct
3. Fix any template literal issues

**Manual updating is safer and recommended.**
