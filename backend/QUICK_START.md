# Quick Start Guide

## Prerequisites Check

- [x] Supabase project created
- [x] API keys obtained (OpenAI, Groq, Gemini, Cohere)
- [ ] Supabase Service Role Key (get from dashboard)
- [ ] Supabase JWT Secret (get from dashboard)
- [ ] Database schema run (SQL script)

## Step 1: Get Missing Supabase Keys

### Service Role Key
1. Go to: https://brcfzyyvgotqvgjwqkov.supabase.co/project/settings/api
2. Find **"service_role"** key (it's a secret key, different from anon key)
3. Copy it

### JWT Secret
1. Same page: **Settings** → **API**
2. Scroll to **"JWT Settings"**
3. Click **"Reveal"** on JWT Secret
4. Copy it

## Step 2: Create .env File

In `backend/` directory, create `.env`:

```bash
# Copy the template from SETUP_YOUR_CREDENTIALS.md
# Replace YOUR_SERVICE_ROLE_KEY_HERE and YOUR_JWT_SECRET_HERE
```

## Step 3: Setup Database

1. Open Supabase Dashboard → SQL Editor
2. Copy contents of `backend/database/schema.sql`
3. Paste and Run

## Step 4: Install & Run

```bash
cd backend
pip install -r requirements.txt
python main.py
```

## Step 5: Test

```bash
# Health check
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","timestamp":"...","service":"LifeMemory AI API"}
```

## Troubleshooting

### "SUPABASE_SERVICE_ROLE_KEY must be set"
→ Get it from Supabase Dashboard → Settings → API

### "SUPABASE_JWT_SECRET must be set"
→ Get it from Supabase Dashboard → Settings → API → JWT Settings

### "Required tables not found"
→ Run the SQL schema in Supabase SQL Editor

### "No LLM provider available"
→ Check that at least one of OPENAI_API_KEY, GROQ_API_KEY, or GEMINI_API_KEY is set

### "COHERE_API_KEY must be set"
→ Since USE_COHERE=true, you need Cohere API key (you have it, just make sure it's in .env)

