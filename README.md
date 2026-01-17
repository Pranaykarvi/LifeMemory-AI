# LifeMemory AI

<div align="center">

![LifeMemory AI](https://img.shields.io/badge/LifeMemory-AI-blue?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=next.js)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green?style=for-the-badge&logo=supabase)

**A privacy-first personal journaling and memory system with AI-powered reflection capabilities**

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [Deployment](#-deployment) • [API Documentation](#-api-documentation)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Deployment](#-deployment)
- [Security](#-security)
- [Development](#-development)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

LifeMemory AI is a production-grade personal journaling system that combines traditional journaling with AI-powered memory retrieval and pattern analysis. Built with privacy-first principles, it uses advanced RAG (Retrieval-Augmented Generation) techniques to help users reflect on their experiences, identify patterns, and gain insights from their journal entries.

### Key Principles

- **🔒 Privacy-First**: Strict user isolation, no cross-user data access, no training on user data
- **🧠 Evidence-Grounded**: All AI responses are based solely on retrieved journal entries
- **⏰ Temporal Intelligence**: Time, recency, and emotional context matter in retrieval
- **🔄 Agent-Based Reasoning**: Multi-node LangGraph workflow for sophisticated query processing
- **🚀 Production-Ready**: FastAPI, Docker, comprehensive error handling, MLOps integration

---

## ✨ Features

### Core Features

- **📝 Daily Journaling**: One entry per day with mood tracking
- **🔍 Semantic Search**: Find entries by meaning, not just keywords
- **🤖 AI Memory Assistant**: Ask questions about your journal entries
- **📊 Pattern Detection**: Identify trends in emotions, productivity, and habits
- **📅 Calendar View**: Visual calendar showing days with entries
- **🎨 Mood Tracking**: Track emotional states with emoji-based moods
- **🔐 Secure Authentication**: Supabase Auth with JWT verification

### AI Capabilities

- **Intent Classification**: Automatically classifies queries (reflection, pattern, recall, etc.)
- **Hybrid Retrieval**: Combines vector similarity, temporal weighting, and mood filtering
- **Temporal Pattern Analysis**: Analyzes patterns across time periods
- **Evidence-Based Answers**: All responses grounded in retrieved journal entries
- **Multi-LLM Fallback**: Automatic failover between OpenAI, Gemini, and Groq

### Technical Features

- **Vector Embeddings**: pgvector for efficient similarity search
- **Row Level Security**: Database-level user isolation
- **Async Processing**: Non-blocking embedding generation
- **Structured Logging**: Request tracing and observability
- **Health Checks**: Production-ready monitoring
- **CORS Support**: Secure cross-origin requests

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (Next.js Frontend - Vercel)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS + JWT
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (Render)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   API Layer  │  │   Auth Layer │  │  LangGraph Pipeline  │  │
│  │              │  │              │  │                      │  │
│  │ • /journal   │  │ • JWT Verify │  │ 1. Intent Classifier │  │
│  │ • /ask       │  │ • User ID    │  │ 2. Memory Retriever  │  │
│  │ • /insights  │  │ • RLS Check  │  │ 3. Pattern Analyzer  │  │
│  │ • /health    │  │              │  │ 4. Answer Synthesizer│  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                     │              │
│         └─────────────────┴─────────────────────┘              │
│                            │                                    │
│         ┌───────────────────┴───────────────────┐              │
│         │                                       │              │
│  ┌──────▼──────┐                    ┌──────────▼──────┐        │
│  │  Retrieval  │                    │   Embeddings   │        │
│  │   System    │                    │     Service     │        │
│  │             │                    │                 │        │
│  │ • Hybrid    │                    │ • OpenAI        │        │
│  │ • Temporal  │                    │ • Cohere       │        │
│  │ • Mood      │                    │ • Async Gen     │        │
│  └──────┬──────┘                    └──────────┬──────┘        │
└─────────┼───────────────────────────────────────┼───────────────┘
          │                                      │
          │ PostgreSQL + pgvector                │
          ▼                                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Supabase PostgreSQL Database                   │
│  ┌──────────────────┐         ┌──────────────────────┐     │
│  │    journals      │         │ journal_embeddings   │     │
│  │                  │         │                      │     │
│  │ • id             │         │ • journal_id (FK)    │     │
│  │ • user_id        │         │ • embedding (vector) │     │
│  │ • entry_date     │         │ • metadata (jsonb)   │     │
│  │ • content        │         │ • entry_date         │     │
│  │ • mood           │         │                      │     │
│  │ • created_at     │         │                      │     │
│  │ • updated_at     │         │                      │     │
│  └──────────────────┘         └──────────────────────┘     │
│                                                              │
│  Row Level Security (RLS) enforced on all tables            │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

#### Journal Entry Creation Flow

```
User Input → Frontend → POST /journal/save
    ↓
Backend validates JWT → Extract user_id
    ↓
UPSERT to journals table (ON CONFLICT DO UPDATE)
    ↓
Background Task: Generate Embedding
    ↓
Delete old embeddings for (user_id, entry_date)
    ↓
Generate embedding (OpenAI/Cohere)
    ↓
Store in journal_embeddings table
    ↓
Return success to user
```

#### Memory Query Flow (LangGraph Pipeline)

```
User Question → POST /ask
    ↓
JWT Verification → Extract user_id
    ↓
┌─────────────────────────────────────────┐
│      LangGraph Agent Pipeline           │
├─────────────────────────────────────────┤
│                                         │
│  1. Intent Classifier                   │
│     → Classify: reflection/pattern/     │
│        recall/temporal_comparison/advice│
│                                         │
│  2. Memory Retriever                    │
│     → Extract temporal filters          │
│     → Extract mood filters              │
│     → Hybrid retrieval (vector +        │
│        temporal + mood weighting)       │
│                                         │
│  3. Evidence Safety Check               │
│     → Validate minimum evidence         │
│     → Check relevance scores            │
│                                         │
│  4. Temporal Pattern Analyzer           │
│     → Analyze time-of-day patterns      │
│     → Analyze day-of-week patterns      │
│     → Analyze mood distribution         │
│                                         │
│  5. Reflection Synthesizer              │
│     → Build context from entries        │
│     → Generate evidence-based answer    │
│     → Return answer + evidence          │
│                                         │
└─────────────────────────────────────────┘
    ↓
Return JSON: {answer, evidence, intent, ...}
```

### Component Architecture

```
backend/
├── api/                    # FastAPI endpoints
│   ├── journal.py         # Journal CRUD operations
│   ├── ask.py             # Memory query endpoint
│   ├── insights.py        # Statistics and insights
│   └── health.py          # Health check
│
├── auth/                   # Authentication
│   └── supabase.py        # JWT verification, OIDC discovery
│
├── config/                 # Configuration
│   └── settings.py         # Centralized settings (pydantic)
│
├── database/               # Database layer
│   ├── connection.py      # Connection pooling (asyncpg)
│   └── schema.sql         # Database schema
│
├── embeddings/             # Embedding generation
│   └── embedder.py        # OpenAI/Cohere embedding service
│
├── graph/                  # LangGraph agent pipeline
│   └── memory_graph.py    # Multi-node state machine
│
├── llm/                    # LLM routing
│   └── router.py          # Multi-provider fallback router
│
├── retrieval/              # Hybrid retrieval
│   └── hybrid_retriever.py # Vector + temporal + mood retrieval
│
├── middleware/             # Request middleware
│   └── logging.py         # Request ID, structured logging
│
└── utils/                  # Utilities
    └── safety.py          # Production safety checks
```

---

## 🛠️ Technology Stack

### Backend

- **Framework**: FastAPI 0.109+ (async Python)
- **Database**: Supabase PostgreSQL with pgvector extension
- **Authentication**: Supabase Auth (JWT with OIDC discovery)
- **LLM Orchestration**: LangChain + LangGraph
- **LLM Providers**: OpenAI (primary), Gemini (fallback), Groq (disabled)
- **Embeddings**: Cohere `embed-v3` (default, 1024 dim) or OpenAI `text-embedding-3-large`
- **Vector Search**: pgvector with cosine similarity
- **Async**: asyncpg for database, httpx for HTTP
- **Configuration**: pydantic-settings
- **Logging**: Structured JSON logging with request IDs

### Frontend

- **Framework**: Next.js 15 (React)
- **UI**: Tailwind CSS, shadcn/ui components
- **Authentication**: Supabase Auth client
- **State Management**: React hooks
- **Deployment**: Vercel

### Infrastructure

- **Backend Hosting**: Render (Docker)
- **Frontend Hosting**: Vercel
- **Database**: Supabase PostgreSQL
- **Containerization**: Docker, Docker Compose

### MLOps (Optional)

- **Tracking**: MLflow
- **Drift Detection**: Evidently AI
- **Evaluation**: Ragas

---

## 📁 Project Structure

```
ai-journal/
├── backend/                    # FastAPI backend
│   ├── api/                   # API endpoints
│   ├── auth/                  # Authentication
│   ├── config/                # Configuration
│   ├── database/              # Database layer
│   ├── embeddings/            # Embedding service
│   ├── graph/                 # LangGraph pipeline
│   ├── llm/                   # LLM router
│   ├── retrieval/             # Hybrid retrieval
│   ├── middleware/            # Request middleware
│   ├── utils/                 # Utilities
│   ├── main.py                # FastAPI app entry point
│   ├── Dockerfile             # Docker configuration
│   ├── requirements.prod.txt  # Production dependencies
│   └── requirements.ml.txt    # ML/evaluation dependencies
│
├── frontend/                  # Next.js frontend
│   ├── app/                   # Next.js app directory
│   ├── components/            # React components
│   ├── lib/                   # Utilities and API client
│   ├── package.json           # Node dependencies
│   └── vercel.json            # Vercel configuration
│
├── .env.example              # Environment variable template
├── README.md                 # This file
├── LICENSE                   # License file
└── DEMO_ENTRIES.md           # Demo entries for testing
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ (backend)
- Node.js 18+ (frontend)
- Supabase account
- OpenAI API key (or Cohere API key)
- Docker (optional, for containerized deployment)

### 1. Clone the Repository

```bash
git clone https://github.com/Pranaykarvi/LifeMemory-AI.git
cd ai-journal
```

### 2. Backend Setup

#### Install Dependencies

```bash
cd backend
pip install -r requirements.prod.txt
```

#### Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
DATABASE_URL=postgresql://postgres:password@host:port/dbname

# Embeddings (choose one)
USE_COHERE=true
COHERE_API_KEY=your-cohere-key
# OR
OPENAI_API_KEY=your-openai-key

# LLM (at least one required)
OPENAI_API_KEY=your-openai-key
# Optional fallbacks
GEMINI_API_KEY=your-gemini-key

# Application
ENV=development
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000
```

#### Database Setup

1. Go to your Supabase project dashboard
2. Open the SQL Editor
3. Run the schema from `backend/database/schema.sql`:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create journals table
CREATE TABLE IF NOT EXISTS journals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    entry_date DATE NOT NULL,
    content TEXT NOT NULL,
    mood TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE (user_id, entry_date)
);

-- Create journal_embeddings table
CREATE TABLE IF NOT EXISTS journal_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_id UUID NOT NULL REFERENCES journals(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    entry_date DATE NOT NULL,
    embedding vector(1024),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(journal_id),
    UNIQUE(user_id, entry_date)
);

-- Enable Row Level Security
ALTER TABLE journals ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_embeddings ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY user_owns_journals ON journals
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY user_owns_embeddings ON journal_embeddings
    FOR ALL USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_journals_user_id ON journals(user_id);
CREATE INDEX IF NOT EXISTS idx_journals_entry_date ON journals(entry_date DESC);
CREATE INDEX IF NOT EXISTS idx_journals_user_entry_date ON journals(user_id, entry_date DESC);
CREATE INDEX IF NOT EXISTS idx_journal_embeddings_user_id ON journal_embeddings(user_id);
CREATE INDEX IF NOT EXISTS idx_journal_embeddings_entry_date ON journal_embeddings(entry_date);
```

#### Run the Backend

```bash
python main.py
```

The backend will start on `http://localhost:8000`

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Configure Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Run the Frontend

```bash
npm run dev
```

The frontend will start on `http://localhost:3000`

### 4. Test the Application

1. Open `http://localhost:3000` in your browser
2. Sign up for a new account
3. Create your first journal entry
4. Wait a few seconds for embedding generation
5. Ask a question in the memory chat (e.g., "What patterns do you notice in my emotions?")

---

## ⚙️ Configuration

### Environment Variables

#### Backend (`.env`)

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `SUPABASE_URL` | Yes | Supabase project URL | - |
| `SUPABASE_ANON_KEY` | Yes | Supabase anonymous key | - |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Supabase service role key | - |
| `SUPABASE_JWT_SECRET` | Yes | JWT secret for token verification | - |
| `DATABASE_URL` | Yes | PostgreSQL connection string | - |
| `USE_COHERE` | No | Use Cohere for embeddings | `true` |
| `COHERE_API_KEY` | Conditional | Cohere API key (if `USE_COHERE=true`) | - |
| `OPENAI_API_KEY` | Conditional | OpenAI API key (for embeddings or LLM) | - |
| `GEMINI_API_KEY` | No | Gemini API key (fallback LLM) | - |
| `ENV` | No | Environment (development/production) | `production` |
| `LOG_LEVEL` | No | Logging level | `INFO` |
| `ALLOWED_ORIGINS` | No | CORS allowed origins (comma-separated) | `http://localhost:3000` |

#### Frontend (`.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | Supabase anonymous key |
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL |

### LLM Provider Configuration

The system supports multiple LLM providers with automatic fallback:

1. **OpenAI** (Primary): `gpt-4o-mini` - Fast, reliable, cost-effective
2. **Gemini** (Fallback): `gemini-1.5-flash-002` - Google's model
3. **Groq** (Disabled): Requires incompatible `langchain-core` version

The router automatically selects the first available provider. If all fail, it returns a safe fallback message.

### Embedding Provider Configuration

- **Default**: Cohere `embed-v3` (1024 dimensions, cost-effective)
- **Fallback**: OpenAI `text-embedding-3-large` (3072 dimensions, if Cohere unavailable)

---

## 📚 API Documentation

### Base URL

- **Development**: `http://localhost:8000`
- **Production**: Your Render backend URL

### Authentication

All endpoints (except `/health`) require authentication via JWT token:

```
Authorization: Bearer <your-jwt-token>
```

### Endpoints

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### Save Journal Entry

```http
POST /journal/save
Content-Type: application/json
Authorization: Bearer <token>

{
  "content": "Today was a great day...",
  "mood": "happy",
  "entry_date": "2024-01-01"
}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "entry_date": "2024-01-01",
  "content": "Today was a great day...",
  "mood": "happy",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Note**: This is an UPSERT operation. If an entry exists for the same `user_id` and `entry_date`, it will be updated.

#### Get Journal Entry

```http
GET /journal/get?entry_date=2024-01-01
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "entry_date": "2024-01-01",
  "content": "Today was a great day...",
  "mood": "happy",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### List Journal Entries

```http
GET /journal/list?page=1&page_size=20
Authorization: Bearer <token>
```

**Response:**
```json
{
  "entries": [
    {
      "id": "uuid",
      "entry_date": "2024-01-01",
      "content": "Today was a great day...",
      "mood": "happy",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

#### Get Days with Entries

```http
GET /journal/days-with-entries?month=2024-01
Authorization: Bearer <token>
```

**Response:**
```json
{
  "dates": ["2024-01-01", "2024-01-05", "2024-01-10"]
}
```

#### Ask Question (Memory Query)

```http
POST /ask
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": "What patterns do you notice in my emotions?"
}
```

**Response:**
```json
{
  "answer": "Based on your journal entries, I notice...",
  "evidence": [
    {
      "id": "uuid",
      "date": "2024-01-01",
      "content": "Today was a great day...",
      "mood": "happy",
      "score": 0.85
    }
  ],
  "intent": "pattern",
  "retrieved_count": 5,
  "llm_provider": "openai"
}
```

#### Get Insights

```http
GET /insights/summary
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_entries": 50,
  "total_words": 5000,
  "mood_distribution": {
    "happy": 20,
    "sad": 10,
    "anxious": 5
  },
  "most_active_day": "Monday",
  "average_entry_length": 100
}
```

---

## 🗄️ Database Schema

### Journals Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Journal entry ID |
| `user_id` | UUID | NOT NULL | User ID (from Supabase Auth) |
| `entry_date` | DATE | NOT NULL | Entry date (YYYY-MM-DD) |
| `content` | TEXT | NOT NULL | Journal entry content |
| `mood` | TEXT | NULL | Mood label (e.g., "happy", "sad") |
| `created_at` | TIMESTAMPTZ | DEFAULT now() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT now() | Last update timestamp |

**Constraints:**
- `UNIQUE (user_id, entry_date)` - One entry per user per day

### Journal Embeddings Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Embedding ID |
| `journal_id` | UUID | NOT NULL, FK | Reference to journals table |
| `user_id` | UUID | NOT NULL | User ID (for RLS) |
| `entry_date` | DATE | NOT NULL | Entry date (for filtering) |
| `embedding` | vector(1024) | NULL | Vector embedding (pgvector) |
| `metadata` | JSONB | DEFAULT '{}' | Additional metadata |
| `created_at` | TIMESTAMPTZ | DEFAULT now() | Creation timestamp |

**Constraints:**
- `UNIQUE(journal_id)` - One embedding per journal
- `UNIQUE(user_id, entry_date)` - One embedding per user per day

**Metadata Structure:**
```json
{
  "mood": "happy",
  "entry_date": "2024-01-01",
  "week": 1,
  "month": 1,
  "year": 2024
}
```

### Row Level Security (RLS)

Both tables have RLS enabled with policies:

```sql
-- Journals
CREATE POLICY user_owns_journals ON journals
    FOR ALL USING (auth.uid() = user_id);

-- Embeddings
CREATE POLICY user_owns_embeddings ON journal_embeddings
    FOR ALL USING (auth.uid() = user_id);
```

This ensures users can only access their own data, even if application-level filtering fails.

---

## 🚢 Deployment

### Backend Deployment (Render)

1. **Create a new Web Service** on Render
2. **Connect your GitHub repository**
3. **Configure the service:**
   - **Root Directory**: `backend`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Instance Type**: Free tier or higher

4. **Set Environment Variables:**
   - All variables from `.env` (see Configuration section)
   - `ALLOWED_ORIGINS`: Your Vercel frontend URL (e.g., `https://your-app.vercel.app`)

5. **Deploy**: Render will automatically build and deploy

### Frontend Deployment (Vercel)

1. **Import your GitHub repository** to Vercel
2. **Configure the project:**
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

3. **Set Environment Variables:**
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_API_URL`: Your Render backend URL

4. **Deploy**: Vercel will automatically deploy on push

### Connecting Frontend and Backend

1. **Update Vercel Environment Variables:**
   - Set `NEXT_PUBLIC_API_URL` to your Render backend URL

2. **Update Render Environment Variables:**
   - Set `ALLOWED_ORIGINS` to your Vercel frontend URL

3. **Test the Connection:**
   - Open your Vercel frontend
   - Check browser console for CORS errors
   - Test authentication and API calls

### Docker Deployment (Local/Server)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
cd backend
docker build -t lifememory-backend .
docker run -p 8000:8000 --env-file .env lifememory-backend
```

---

## 🔒 Security

### Authentication & Authorization

- **JWT Verification**: Every request is authenticated via Supabase JWT
- **OIDC Discovery**: Dynamic JWKS URI discovery for token verification
- **User Isolation**: All queries are scoped to `user_id` from JWT
- **Row Level Security**: Database-level enforcement of user isolation

### Data Privacy

- **No Cross-User Access**: Impossible by design (RLS + explicit filtering)
- **No Data Training**: User data is never used for training
- **Privacy-Preserving Logs**: No journal content in logs, user IDs truncated
- **Secure Storage**: All data encrypted at rest (Supabase)

### API Security

- **CORS**: Configured for specific origins only (no wildcards in production)
- **Rate Limiting**: Can be added via middleware (not included by default)
- **Input Validation**: Pydantic models validate all inputs
- **SQL Injection Protection**: Parameterized queries only

### Best Practices

- Never commit `.env` files
- Use strong, unique API keys
- Rotate keys regularly
- Monitor for suspicious activity
- Keep dependencies updated

---

## 💻 Development

### Running in Development Mode

```bash
# Backend
cd backend
ENV=development python main.py

# Frontend
cd frontend
npm run dev
```

### Code Structure

- **Type Hints**: All functions have type hints
- **Docstrings**: All functions and classes documented
- **Error Handling**: Comprehensive error handling throughout
- **Async/Await**: Proper async patterns for I/O operations
- **Logging**: Structured logging with request IDs

### Adding New Features

1. **API Endpoints**: Add to `backend/api/`
2. **Database Changes**: Update `backend/database/schema.sql` and create migration
3. **Frontend Components**: Add to `frontend/components/`
4. **LLM Prompts**: Update `backend/graph/memory_graph.py`

### Testing

```bash
# Backend tests (if available)
cd backend
pytest

# Frontend tests (if available)
cd frontend
npm test
```

---

## 🧪 Testing

### Manual Testing

1. **Create Test Entries**: Use entries from `DEMO_ENTRIES.md`
2. **Test Queries**: Try different intent types:
   - Reflection: "Why was I feeling burned out?"
   - Pattern: "What patterns do you notice in my emotions?"
   - Recall: "What happened last week?"
   - Temporal Comparison: "How was January different from December?"
   - Advice: "What should I do about my work stress?"

3. **Test Edge Cases**:
   - Empty journal entries
   - Very long entries
   - Special characters
   - Multiple entries per day (should update, not create)

### Integration Testing

- Test authentication flow
- Test journal creation and retrieval
- Test memory queries with various intents
- Test error handling (invalid tokens, missing data, etc.)

---

## 🐛 Troubleshooting

### Common Issues

#### Backend won't start

- **Check environment variables**: Ensure all required variables are set
- **Check database connection**: Verify `DATABASE_URL` is correct
- **Check API keys**: Ensure at least one LLM provider key is set

#### CORS errors

- **Check `ALLOWED_ORIGINS`**: Ensure frontend URL is included
- **Check backend logs**: Look for CORS-related errors
- **Verify headers**: Ensure `Authorization` header is sent

#### Authentication errors

- **Check JWT token**: Verify token is valid and not expired
- **Check Supabase credentials**: Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- **Check JWT secret**: Verify `SUPABASE_JWT_SECRET` matches Supabase

#### Embedding generation fails

- **Check API keys**: Verify `COHERE_API_KEY` or `OPENAI_API_KEY` is set
- **Check database**: Ensure `journal_embeddings` table exists
- **Check logs**: Look for embedding generation errors

#### Memory queries return empty results

- **Wait for embeddings**: Embeddings are generated asynchronously
- **Check entry count**: Need at least 2-3 entries for pattern queries
- **Check relevance scores**: Low scores may indicate poor matches

### Debug Mode

Enable debug logging:

```bash
# Backend
LOG_LEVEL=DEBUG python main.py

# Check logs for detailed information
```

---

## 📝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Follow code style and add tests
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**: Describe your changes clearly

### Code Style

- **Python**: Follow PEP 8, use type hints, add docstrings
- **TypeScript**: Follow ESLint rules, use TypeScript types
- **Commits**: Use clear, descriptive commit messages

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 🙏 Acknowledgments

- **FastAPI** for the excellent async framework
- **Supabase** for the database and auth infrastructure
- **LangChain/LangGraph** for the agent orchestration
- **OpenAI/Cohere** for embeddings and LLM capabilities
- **Next.js** for the frontend framework

---

## 📞 Support

For issues, questions, or contributions:

- **GitHub Issues**: [Create an issue](https://github.com/Pranaykarvi/LifeMemory-AI/issues)
- **Documentation**: See this README and inline code documentation

---

<div align="center">

**Built with ❤️ for personal reflection and growth**

[⬆ Back to Top](#lifememory-ai)

</div>

