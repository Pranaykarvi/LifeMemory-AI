# LifeMemory AI Backend - Setup Guide

## Prerequisites

1. Python 3.11+
2. Supabase account and project
3. OpenAI API key (or Cohere API key)
4. Docker and Docker Compose (for containerized deployment)

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
cd backend
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Supabase

#### a. Create Supabase Project
- Go to [supabase.com](https://supabase.com)
- Create a new project
- Note your project URL and API keys

#### b. Set Up Database Schema

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy the contents of `database/schema.sql`
4. Paste and run the SQL script

This will:
- Enable pgvector extension
- Create `journals` and `journal_embeddings` tables
- Set up Row Level Security (RLS) policies
- Create necessary indexes

#### c. Get Database Connection String

1. Go to Settings > Database
2. Find "Connection string" section
3. Copy the connection string (use "Session mode" or "Transaction mode")
4. It should look like: `postgresql://postgres.[project-ref]:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres`

#### d. Get JWT Secret

1. Go to Settings > API
2. Find "JWT Secret" (under "Project API keys")
3. Copy the JWT secret

### 4. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSION=3072

# LLM Configuration
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.3

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000
```

### 5. Verify Database Setup

Run the application to verify database connection:

```bash
python main.py
```

The application will:
- Connect to Supabase
- Verify pgvector extension is enabled
- Check that required tables exist

### 6. Test the API

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Create Journal Entry (requires auth token)
```bash
curl -X POST http://localhost:8000/journal/add \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Today was a great day!",
    "mood": "happy"
  }'
```

## Docker Deployment

### Build and Run

```bash
docker-compose up --build
```

This will start:
- Backend API (port 8000)
- Redis (port 6379) - for background jobs
- MLflow (port 5000) - for MLOps tracking

### Environment Variables for Docker

Make sure your `.env` file is in the `backend` directory. Docker Compose will automatically load it.

## Production Deployment

### Render / Railway / AWS EC2

1. Set all environment variables in your platform's dashboard
2. Use the Dockerfile for containerized deployment
3. Ensure `DATABASE_URL` is set correctly
4. Configure CORS for your frontend domain

### Environment Variables Checklist

- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_KEY`
- [ ] `SUPABASE_SERVICE_ROLE_KEY`
- [ ] `SUPABASE_JWT_SECRET`
- [ ] `DATABASE_URL` (or `SUPABASE_DB_PASSWORD`)
- [ ] `OPENAI_API_KEY` (or `COHERE_API_KEY` if using Cohere)
- [ ] `LLM_MODEL`
- [ ] `ALLOWED_ORIGINS`

## Troubleshooting

### Database Connection Issues

- Verify `DATABASE_URL` is correct
- Check that your Supabase project is active
- Ensure the database password is correct

### RLS Policy Issues

- Verify RLS is enabled on both tables
- Check that policies are created correctly
- Ensure JWT tokens are being verified properly

### Embedding Generation Fails

- Check OpenAI API key is valid
- Verify API quota/limits
- Check logs for specific error messages

### LangGraph Agent Issues

- Verify LangChain/LangGraph versions are compatible
- Check that OpenAI API key has access to the specified model
- Review graph state transitions in logs

## Next Steps

1. Test all API endpoints
2. Set up monitoring and logging
3. Configure MLOps tracking (MLflow)
4. Set up drift detection (Evidently AI)
5. Configure RAG evaluation (Ragas)

## Security Notes

- Never commit `.env` file to version control
- Use service role key only for server-side operations
- Always verify JWT tokens on every request
- RLS policies provide defense-in-depth security
- All queries explicitly filter by `user_id`

