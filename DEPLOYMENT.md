# Deployment Guide for LegalX Knowledge Centre

This guide provides step-by-step instructions for deploying LegalX to production using Railway (backend) and Vercel (frontend).

## Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│           LegalX in Production                  │
├─────────────────────────────────────────────────┤
│                                                 │
│  Frontend (Vercel)    Backend (Railway)         │
│  https://legalx-kc.vercel.app                   │
│  React + Vite ────────────────────► FastAPI     │
│                                     │           │
│  Browser              ┌─────────────┘           │
│  requests  ────────────────────────► /api/*     │
│                         API                     │
│                                     ▼           │
│                              Gemini API         │
│                              ChromaDB           │
│                              (local storage)    │
└─────────────────────────────────────────────────┘
```

---

## Pre-Deployment Checklist

- [ ] GitHub account and repository created
- [ ] Code pushed to `main` branch
- [ ] All sensitive data in `.env` (not in git)
- [ ] `.gitignore` includes `.env`, `node_modules`, `__pycache__`
- [ ] Backend tested locally with `python main.py`
- [ ] Frontend tested locally with `npm run dev`
- [ ] API responding on `http://localhost:8000/api/health`
- [ ] All 5 topics showing on frontend

---

## Part 1: Backend Deployment to Railway

Railway is a modern deployment platform with free tier, perfect for this project.

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click "Start Project" (free)
3. Sign up with GitHub (recommended)
4. Authorize Railway to access your repositories

### Step 2: Create Railway Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Search for your `legalx-knowledge-centre` repository
4. Click to select it
5. Railway auto-detects it's a Python project

### Step 3: Configure Environment Variables

Railway builds and deploys automatically, but needs your API key:

1. In Railway dashboard, go to project → "Variables"
2. Click "Add Variable"
3. Add these environment variables:

| Key | Value | Description |
|-----|-------|-------------|
| `GEMINI_API_KEY` | `your-gemini-key` | Get from [aistudio.google.com](https://aistudio.google.com) |
| `GOOGLE_API_KEY` | `your-google-key` | Same as above (backup) |

**Getting Gemini API Key:**
- Go to [Google AI Studio](https://aistudio.google.com)
- Click "Get API Key" → "Create new Secret Key"
- Copy the key
- Paste into Railway Variables

### Step 4: Configure Build & Start Commands

Railway should auto-detect, but if not, set:

**Build Command:**
```
pip install -r backend/requirements.txt
```

**Start Command:**
```
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 5: Monitor Deployment

1. Go to Deployments tab
2. Watch the logs as Railway builds and starts your app
3. Look for: `Uvicorn running on http://0.0.0.0:8000`

### Step 6: Get Backend URL

1. Click on your service in Railway
2. In Settings, copy the "Service URL" (looks like: `https://your-backend-railway.railway.app`)
3. **Note this URL** - you'll need it for frontend

### Step 7: Test Backend Deployment

```bash
# Test the deployed backend
curl https://your-backend-railway.railway.app/api/health

# Should return:
# {"status":"healthy","documents_indexed":77,"topics_available":[...]}
```

---

## Part 1.5: Alternative Backend Deployment to Render (Free Tier)

Render offers a fully-featured free tier for hosting web services and supports Docker deployments.

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Click "Sign Up" and choose GitHub.

### Step 2: Create a Web Service
1. Click **New +** at the top right and select **Web Service**.
2. Select **Build and deploy from a Git repository** (or select the connected GitHub repository `LegalX`).
3. Connect the `LegalX` repository.

### Step 3: Configure Project
Configure the following settings on the creation screen:
- **Name**: `legalx-backend`
- **Region**: Select the region closest to you.
- **Branch**: `main`
- **Runtime**: `Docker` *(Render will automatically detect the root `Dockerfile` and build the container, guaranteeing a consistent Python runtime env)*
- **Instance Type**: Select **Free**.

### Step 4: Configure Environment Variables
1. Scroll down to **Advanced** or find the **Environment Variables** section.
2. Click **Add Environment Variable** and add the following keys:

| Key | Value | Description |
|-----|-------|-------------|
| `GEMINI_API_KEY` | `your-gemini-key` | Your Google Gemini API Key |
| `GOOGLE_API_KEY` | `your-gemini-key` | Duplicate of Gemini key for SDK backup |

### Step 5: Deploy & Monitor
1. Click **Create Web Service** (or **Deploy**).
2. Monitor Render's build and deployment log. It will build the Docker container and display `Uvicorn running on http://0.0.0.0:8000` (respecting Render's dynamic `$PORT` assignment).
3. Once the service shows "Live", copy the Render Web Service URL (looks like: `https://legalx-backend.onrender.com`).
4. **Note this URL** - you will need to set it as `VITE_API_URL` when deploying the frontend on Vercel.

---

## Part 2: Frontend Deployment to Vercel

Vercel has zero-config deployment for Vite projects.

### Step 1: Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Click "Sign Up"
3. Sign up with GitHub (recommended)
4. Authorize Vercel to access repositories

### Step 2: Import Project

1. Click "New Project"
2. Click "Import Git Repository"
3. Search for and select `legalx-knowledge-centre`
4. Click "Import"

### Step 3: Configure Project

1. **Framework Preset:** Select "Vite"
2. **Root Directory:** Set to `./frontend`
3. **Build Command:** `npm run build`
4. **Output Directory:** `dist`

### Step 4: Add Environment Variables

1. Go to "Environment Variables"
2. Add variable:

| Name | Value |
|------|-------|
| `VITE_API_URL` | `https://your-backend-railway.railway.app` |

(Replace with your actual Railway backend URL from Part 1)

### Step 5: Deploy

1. Click "Deploy"
2. Vercel builds and deploys automatically
3. Wait for success message (should take 2-3 minutes)

### Step 6: Get Frontend URL

1. Deployment complete page shows your frontend URL
2. Usually: `https://legalx-knowledge-centre.vercel.app`
3. Click to view your deployed app!

---

## Part 3: Verify Full Stack Deployment

### Frontend Checks

1. Open your Vercel URL
2. Should see 5 legal topic cards
3. Click on a card
4. Should load topic details
5. All tabs should work (Summary, Key Info, Audio, Chat)

### Backend API Checks

```bash
# Health check
curl https://your-backend.railway.app/api/health

# Get topics
curl https://your-backend.railway.app/api/topics

# Get specific topic
curl https://your-backend.railway.app/api/topics/pocso_act

# Test chat (replace URL)
curl -X POST https://your-backend.railway.app/api/topics/pocso_act/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What is POCSO?","history":[]}'
```

### Chat Q&A Test

1. Go to deployed frontend
2. Click on a topic
3. Go to "Chat" tab
4. Ask a question
5. Should get an answer with source citations

### Audio Test

1. Go to "Audio" tab
2. Click Play
3. Should play audio

---

## Troubleshooting

### Issue: "502 Bad Gateway" on Backend

**Cause:** Backend service not running
**Solution:**
1. Check Railway Deployments tab for errors
2. View logs: `cd backend && python main.py` (test locally first)
3. Ensure GEMINI_API_KEY is set in Railway Variables
4. Wait 2-3 minutes for initial deployment startup

### Issue: Frontend Shows "Failed to get response"

**Cause:** Wrong API URL or CORS issues
**Solution:**
1. Check `VITE_API_URL` environment variable in Vercel
2. Open browser DevTools Console (F12)
3. Check Network tab - what URL is it trying to call?
4. Ensure backend URL is correct and `https://` not `http://`

### Issue: "API Rate Limit" Errors

**Cause:** Hitting Gemini API rate limits
**Solution:**
1. These are expected on first startup (generating summaries)
2. Errors are graceful - system shows cached defaults
3. After first run, cache is used (no rate limits)
4. Consider upgrading Gemini API plan for production usage

### Issue: Audio Not Loading

**Cause:** edge-tts API issues (network/auth)
**Solution:**
1. Audio generation can fail gracefully
2. System continues without audio files
3. Check backend logs in Railway
4. Consider using a different TTS service

### Issue: "Permission Denied" on Linux

**Cause:** File permissions
**Solution:**
```bash
# In production (Railway), permissions are handled automatically
# Locally, if testing:
chmod +x backend/main.py
```

---

## Environment Variables Reference

### Backend Required Variables

```env
# .env file (backend directory)
GEMINI_API_KEY=AIza...      # Required
GOOGLE_API_KEY=AIza...      # Optional (backup)
```

### Frontend Required Variables

```env
# Set in Vercel dashboard (or .env.local for local dev)
VITE_API_URL=https://your-backend.railway.app
```

---

## Production Best Practices

### 1. Monitoring

- Set up Railway and Vercel alerts for failures
- Monitor error logs regularly
- Track API response times

### 2. Scaling

- If traffic increases, Railway auto-scales (within free tier)
- Consider paid tiers for guaranteed resources
- Implement caching headers for frontend assets

### 3. Security

- Never commit `.env` files with real API keys
- Use GitHub Secrets for CI/CD if needed
- Keep dependencies updated regularly
- Rotate API keys periodically

### 4. Performance

- Frontend is cached by Vercel CDN (fast globally)
- Backend uses FastAPI (high performance)
- Gemini API calls cached (after first run)
- Consider Redis for session storage if needed

### 5. Backup & Recovery

- GitHub is your backup (code only)
- ChromaDB data persists in Railway container
- Audio files regenerate if needed
- Cached JSON regenerates if needed

---

## Rolling Back Deployment

### If Something Goes Wrong on Railway

1. Go to Railway → Deployments
2. Click on a previous working deployment
3. Click "Rollback to this Deployment"
4. Confirm
5. Service reverts to previous version

### If Something Goes Wrong on Vercel

1. Go to Vercel → Deployments
2. Click on a previous working deployment
3. Click "Promote to Production"
4. Site reverts to previous version

---

## Custom Domain (Optional)

### Add Custom Domain to Vercel

1. In Vercel project → Settings → Domains
2. Add your domain (e.g., `legalx.yourdomain.com`)
3. Update DNS records as instructed
4. SSL certificate auto-provisioned

### Add Custom Domain to Railway

1. In Railway project → "Networking"
2. Add custom domain
3. Update DNS CNAME record
4. Verify domain

---

## Monitoring & Logs

### View Railway Logs

1. Railway Dashboard → Select Service
2. Logs tab shows real-time app output
3. Filter by error level
4. Search for specific terms

### View Vercel Logs

1. Vercel Dashboard → Deployments
2. Click deployment → Logs tab
3. Build logs and runtime logs available

---

## Next Steps

1. ✅ Deploy backend to Railway
2. ✅ Deploy frontend to Vercel
3. ✅ Test all features on production URLs
4. ✅ Share deployment links with team/evaluators
5. Update README.md with production URLs
6. Monitor logs and performance
7. Gather user feedback
8. Plan iterations/improvements

---

## Support

### Useful Resources

- [Railway Documentation](https://docs.railway.app/)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Deployment](https://vitejs.dev/guide/static-deploy.html)

### Getting Help

- Check app logs (Railway/Vercel dashboards)
- Test locally first (`python main.py`, `npm run dev`)
- Verify environment variables are set correctly
- Open GitHub issues for bugs

---

**Congratulations!** Your LegalX Knowledge Centre is now live! 🎉
