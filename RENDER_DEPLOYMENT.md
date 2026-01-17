# Render Deployment Guide - Backend

## 📋 Render Form Configuration

### ✅ Already Set (Don't Change)
- **Name**: `LifeMemory-AI` ✓
- **Language**: `Docker` ✓
- **Branch**: `main` ✓
- **Region**: `Oregon (US West)` ✓

### 🔧 Settings to Configure

#### 1. Root Directory
```
backend
```
**Important:** This tells Render to look in the `backend/` folder for the Dockerfile.

#### 2. Instance Type
- **For Testing/Development**: `Free` ($0/month)
  - ⚠️ Spins down after inactivity
  - ⚠️ No SSH access
  - ⚠️ Slower cold starts
  
- **For Production (Recommended)**: `Starter` ($7/month)
  - ✅ Always running
  - ✅ SSH access
  - ✅ Better performance
  - ✅ Zero downtime deployments

**Recommendation:** Start with `Free` to test, then upgrade to `Starter` for production.

#### 3. Environment Variables

Add these environment variables in Render (click "Add Environment Variable" for each):

##### Required - Supabase Configuration
```
SUPABASE_URL=https://brcfzyyvgotqvgjwqkov.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJyY2Z6eXl2Z290cXZnandxa292Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg2Mjk3NTcsImV4cCI6MjA4NDIwNTc1N30.XBF0XtzTm4k40az4dzM4-0Uu1ehXDduwkEhdQODVuh4
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJyY2Z6eXl2Z290cXZnandxa292Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODYyOTc1NywiZXhwIjoyMDg0MjA1NzU3fQ.tYRulZCYc8tQjeTpw_Z5eQ_ad_QxRbvrgrgqkRzBl6M
SUPABASE_JWT_SECRET=EYADi8iEGsrLm6zfzv/fejMsWIwY32+q4JNajHwdw/Y6iVvLVRcFAmRBOLiJEQj+fF2kbCL+uo5eMemGJM1vRg==
```

##### Required - Database
```
DATABASE_URL=postgresql://postgres.brcfzyyvgotqvgjwqkov:MuKaMbIkA2005@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres
```

##### Required - Embedding (Cohere)
```
USE_COHERE=true
COHERE_API_KEY=5rJLG5DNb98pOx8Nh1WflxtHb8Y6tnMOh1kqme3k
EMBEDDING_MODEL=embed-english-v3.0
EMBEDDING_DIMENSION=1024
```

##### Required - LLM (OpenAI Primary)
```
OPENAI_API_KEY=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
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.3
```

##### Optional - LLM Fallbacks (for redundancy)
```
GROQ_API_KEY=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
GEMINI_API_KEY=AIzaSyB7aaWjSnBiC7ejU1-F2qylxhGGp26z5H8
```

##### Required - Application Settings
```
ENV=production
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

**⚠️ IMPORTANT:** Replace `https://your-frontend.vercel.app` with your actual Vercel frontend URL after deployment!

##### Optional - LangGraph Configuration
```
MAX_RETRIEVED_MEMORIES=15
MAX_CONTEXT_TOKENS=4000
MIN_EVIDENCE_THRESHOLD=1
MIN_RELEVANCE_SCORE=0.3
```

## 📝 Step-by-Step Instructions

1. **Set Root Directory**
   - In the "Root Directory" field, type: `backend`

2. **Choose Instance Type**
   - For testing: Select `Free`
   - For production: Select `Starter` ($7/month)

3. **Add Environment Variables**
   - Click "Add Environment Variable" for each variable above
   - Copy the NAME and VALUE exactly as shown
   - **Important:** For `ALLOWED_ORIGINS`, you'll need to update it after you get your Vercel frontend URL

4. **Deploy**
   - Click "Create Web Service" at the bottom
   - Render will build and deploy your backend
   - Wait for deployment to complete (5-10 minutes)

5. **Get Your Backend URL**
   - After deployment, Render will show your service URL
   - It will look like: `https://lifememory-ai.onrender.com`
   - Copy this URL

6. **Update Frontend**
   - Go back to Vercel
   - Update `NEXT_PUBLIC_API_URL` to your Render backend URL
   - Redeploy frontend

7. **Update Backend CORS**
   - Go back to Render
   - Update `ALLOWED_ORIGINS` to include your Vercel frontend URL
   - Render will automatically redeploy

## 🔍 After Deployment

### Check Health Endpoint
```
https://your-backend.onrender.com/health
```
Should return: `{"status": "healthy"}`

### Check Logs
- Go to Render dashboard → Your service → Logs
- Look for: "Application startup complete"
- Check for any errors

## 🐛 Troubleshooting

### Build Fails
- Check that Root Directory is set to `backend`
- Verify Dockerfile exists in `backend/` folder
- Check build logs for specific errors

### Service Won't Start
- Check environment variables are all set
- Verify DATABASE_URL is correct
- Check logs for missing variable errors

### CORS Errors
- Update `ALLOWED_ORIGINS` to include your Vercel frontend URL
- Format: `https://your-app.vercel.app,http://localhost:3000`

### Database Connection Errors
- Verify `DATABASE_URL` is correct
- Check Supabase allows connections from Render IPs
- Try using the pooler URL (port 6543)

## 💰 Cost Estimate

- **Free Tier**: $0/month (for testing)
- **Starter Tier**: $7/month (recommended for production)
- **Total**: $7/month for backend + Vercel free tier for frontend

## ✅ Checklist

Before clicking "Create Web Service", verify:
- [ ] Root Directory = `backend`
- [ ] Instance Type selected
- [ ] All required environment variables added
- [ ] `ALLOWED_ORIGINS` includes `http://localhost:3000` (update with Vercel URL later)
- [ ] GitHub repository is connected
- [ ] Branch = `main`

