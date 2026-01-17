# Quick Setup Guide - Your Credentials

## ✅ What You've Provided

- ✅ Supabase Project URL
- ✅ Supabase Publishable (Anon) Key
- ✅ Database Password
- ✅ All API Keys (OpenAI, Groq, Gemini, Cohere)

## ⚠️ What You Still Need

You need to get these from your Supabase Dashboard:

### 1. SUPABASE_SERVICE_ROLE_KEY
1. Go to: https://brcfzyyvgotqvgjwqkov.supabase.co
2. Navigate to: **Settings** → **API**
3. Find **"service_role"** key (NOT the anon key)
4. Copy it - this is different from the publishable key

### 2. SUPABASE_JWT_SECRET
1. In the same **Settings** → **API** page
2. Scroll down to **"JWT Settings"**
3. Find **"JWT Secret"**
4. Click **"Reveal"** and copy it

## 📝 Create Your .env File

Create a file named `.env` in the `backend/` directory with this content:

```bash
# Environment
ENV=production
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Supabase Configuration
SUPABASE_URL=https://brcfzyyvgotqvgjwqkov.supabase.co
SUPABASE_ANON_KEY=sb_publishable_EiWaRCkHw4o4h0x7dlBkKg_j3lrJGA0
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY_HERE
SUPABASE_JWT_SECRET=YOUR_JWT_SECRET_HERE
DATABASE_URL=postgresql://postgres:MuKaMbIkA2005@db.brcfzyyvgotqvgjwqkov.supabase.co:5432/postgres

# Embedding Configuration (Cohere default)
USE_COHERE=true
COHERE_API_KEY=5rJLG5DNb98pOx8Nh1WflxtHb8Y6tnMOh1kqme3k

# OpenAI (fallback for embeddings)
OPENAI_API_KEY=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
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSION=3072

# LLM Configuration (with fallback)
OPENAI_API_KEY=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
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.3

# LLM Fallbacks
GROQ_API_KEY=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
GEMINI_API_KEY=AIzaSyB7aaWjSnBiC7ejU1-F2qylxhGGp26z5H8

# LangGraph Configuration
MAX_RETRIEVED_MEMORIES=15
MAX_CONTEXT_TOKENS=4000
MIN_EVIDENCE_THRESHOLD=1
MIN_RELEVANCE_SCORE=0.3

# MLOps (Optional)
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=life-memory-ai
LANGCHAIN_TRACING_V2=false
LANGCHAIN_PROJECT=life-memory-ai

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0
```

**Replace:**
- `YOUR_SERVICE_ROLE_KEY_HERE` with the service_role key from Supabase
- `YOUR_JWT_SECRET_HERE` with the JWT secret from Supabase

## 🗄️ Database Setup

Before running the app, you need to set up the database schema:

1. Go to your Supabase Dashboard: https://brcfzyyvgotqvgjwqkov.supabase.co
2. Navigate to: **SQL Editor**
3. Click **"New Query"**
4. Copy the entire contents of `backend/database/schema.sql`
5. Paste it into the SQL editor
6. Click **"Run"**

This will create:
- `journals` table
- `journal_embeddings` table
- Row Level Security (RLS) policies
- pgvector extension
- All necessary indexes

## 🚀 Next Steps

1. **Get the missing Supabase keys** (see above)
2. **Create `.env` file** with your credentials
3. **Run database schema** in Supabase SQL Editor
4. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
5. **Start the server:**
   ```bash
   python main.py
   ```

## 🔒 Security Reminder

- ✅ `.env` file is already in `.gitignore` (won't be committed)
- ⚠️ **NEVER** commit your `.env` file to git
- ⚠️ **NEVER** share your API keys publicly
- ⚠️ If you've shared keys, rotate them immediately

## ✅ Verification

Once everything is set up, test the health endpoint:

```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "service": "LifeMemory AI API"
}
```

