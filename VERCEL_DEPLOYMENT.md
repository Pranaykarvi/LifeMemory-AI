# Vercel Deployment Guide

## 🚀 Quick Setup

### 1. Environment Variables

You **must** set these environment variables in Vercel before deployment:

1. Go to your Vercel project: https://vercel.com/dashboard
2. Navigate to: **Settings** → **Environment Variables**
3. Add the following variables:

#### Required Variables:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://brcfzyyvgotqvgjwqkov.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJyY2Z6eXl2Z290cXZnandxa292Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg2Mjk3NTcsImV4cCI6MjA4NDIwNTc1N30.XBF0XtzTm4k40az4dzM4-0Uu1ehXDduwkEhdQODVuh4
NEXT_PUBLIC_API_URL=https://lifememory-ai.onrender.com
```

**Note:** Replace `https://your-backend-url.vercel.app` with your actual backend deployment URL.

### 2. Backend Deployment

The backend needs to be deployed separately. Options:

#### Option A: Deploy Backend to Vercel (Serverless Functions)
- Convert FastAPI endpoints to Vercel serverless functions
- See: https://vercel.com/docs/frameworks/python

#### Option B: Deploy Backend to Railway/Render/Fly.io
- Deploy the FastAPI backend as a separate service
- Update `NEXT_PUBLIC_API_URL` to point to your backend URL

#### Option C: Use Vercel's API Routes (Recommended for Quick Start)
- Create API routes in `frontend/app/api/` that proxy to your backend
- Or deploy backend separately and use its URL

### 3. Build Settings

Vercel should auto-detect Next.js. If not, configure:

- **Framework Preset:** Next.js
- **Root Directory:** `frontend` (if deploying from monorepo)
- **Build Command:** `npm run build` (default)
- **Output Directory:** `.next` (default)

### 4. Monorepo Configuration

If deploying from the root directory, you need to configure Vercel:

1. Go to **Settings** → **General**
2. Set **Root Directory** to `frontend`
3. Or create `vercel.json` in the root:

```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/.next",
  "installCommand": "cd frontend && npm install"
}
```

## 🔧 Troubleshooting

### Build Fails: "Missing Supabase environment variables"

**Solution:** Add `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` in Vercel environment variables.

### Build Fails: "Cannot find module"

**Solution:** Make sure `package.json` is in the `frontend/` directory and dependencies are installed.

### Runtime Error: "Cannot connect to backend"

**Solution:** 
1. Deploy backend separately
2. Update `NEXT_PUBLIC_API_URL` in Vercel environment variables
3. Ensure backend CORS allows your Vercel domain

### Build Succeeds but App Doesn't Work

**Check:**
1. Environment variables are set for **Production** environment
2. `NEXT_PUBLIC_API_URL` points to a deployed backend
3. Backend is running and accessible
4. CORS is configured correctly

## 📝 Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | ✅ Yes | Supabase project URL | `https://xxx.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✅ Yes | Supabase anonymous key | `eyJhbGci...` |
| `NEXT_PUBLIC_API_URL` | ⚠️ Optional | Backend API URL | `https://api.example.com` |

**Note:** Variables starting with `NEXT_PUBLIC_` are exposed to the browser. Never put secrets here.

## 🎯 Recommended Deployment Flow

1. **Deploy Backend First**
   - Deploy FastAPI backend to Railway/Render/Fly.io
   - Get the backend URL

2. **Set Environment Variables in Vercel**
   - Add all `NEXT_PUBLIC_*` variables
   - Set `NEXT_PUBLIC_API_URL` to your backend URL

3. **Deploy Frontend**
   - Connect GitHub repository to Vercel
   - Vercel will auto-deploy on push to `main`

4. **Verify**
   - Check frontend is accessible
   - Test authentication
   - Test API calls

## 🔗 Useful Links

- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Next.js on Vercel](https://vercel.com/docs/frameworks/nextjs)
- [Deploying Python (FastAPI) to Vercel](https://vercel.com/docs/frameworks/python)

