# Connect Frontend (Vercel) to Backend (Render)

## ✅ Backend URL
**Your Render backend is live at:** `https://lifememory-ai.onrender.com`

## 🔧 Step 1: Update Vercel Environment Variables

1. Go to your Vercel project: https://vercel.com/dashboard
2. Navigate to: **Settings** → **Environment Variables**
3. Update `NEXT_PUBLIC_API_URL`:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://lifememory-ai.onrender.com`
   - **Environment**: Production, Preview, Development (select all)
4. Click **Save**

## 🔧 Step 2: Update Render CORS Settings

1. Go to your Render dashboard: https://dashboard.render.com
2. Find your **LifeMemory-AI** service
3. Go to **Environment** tab
4. Find `ALLOWED_ORIGINS` variable
5. Update it to include your Vercel frontend URL:
   ```
   https://your-frontend.vercel.app,http://localhost:3000
   ```
   **Replace `your-frontend.vercel.app` with your actual Vercel domain** (e.g., `life-memory-ai.vercel.app`)

6. Click **Save Changes**
7. Render will automatically redeploy

## 📋 Complete Environment Variables Checklist

### Vercel (Frontend)
- ✅ `NEXT_PUBLIC_SUPABASE_URL` = `https://brcfzyyvgotqvgjwqkov.supabase.co`
- ✅ `NEXT_PUBLIC_SUPABASE_ANON_KEY` = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- ✅ `NEXT_PUBLIC_API_URL` = `https://lifememory-ai.onrender.com` ← **UPDATE THIS**

### Render (Backend)
- ✅ All backend variables (Supabase, API keys, etc.)
- ✅ `ALLOWED_ORIGINS` = `https://your-frontend.vercel.app,http://localhost:3000` ← **UPDATE THIS**

## 🧪 Test the Connection

After updating both:

1. **Test Backend Health:**
   ```
   https://lifememory-ai.onrender.com/health
   ```
   Should return: `{"status": "healthy"}`

2. **Test from Frontend:**
   - Open your Vercel frontend URL
   - Try to sign in
   - Try to save a journal entry
   - Check browser console for any CORS errors

## 🐛 Troubleshooting

### CORS Errors
- Make sure `ALLOWED_ORIGINS` in Render includes your exact Vercel URL (with `https://`)
- Check that the URL matches exactly (no trailing slashes)

### 401 Unauthorized
- Check that `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- Verify Supabase authentication is working

### Connection Refused
- Check that Render service is running (not sleeping)
- Verify the backend URL is correct: `https://lifememory-ai.onrender.com`

