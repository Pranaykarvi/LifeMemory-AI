# LifeMemory AI - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- ✅ Backend is running on `http://localhost:8000`
- ✅ Database schema is set up in Supabase
- ✅ Environment variables configured

### Step 1: Start Backend

```bash
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start Frontend

In a **new terminal**:

```bash
cd frontend
npm run dev
```

Frontend will start on `http://localhost:3000`

### Step 3: Test the Application

1. **Open Browser**: http://localhost:3000
2. **Sign Up**: Create a new account with email/password
3. **Write Journal**: Create your first journal entry
4. **Ask Questions**: Use the memory chat to ask about your entries

## 🔗 How Frontend & Backend Connect

### Authentication Flow
1. User signs in via Supabase Auth (frontend)
2. Supabase returns JWT token
3. Frontend stores token in Supabase client
4. All API calls include token: `Authorization: Bearer <token>`
5. Backend verifies token and extracts `user_id`

### API Communication
- **Frontend** → `lib/api.ts` → **Backend** (`http://localhost:8000`)
- All requests include JWT token automatically
- Backend validates token and enforces user isolation

## 📝 What's Connected

✅ **Authentication**: Supabase Auth ↔ Backend JWT verification  
✅ **Journal Creation**: Frontend editor → `POST /journal/add`  
✅ **Journal Listing**: Frontend sidebar → `GET /journal/list`  
✅ **Memory Chat**: Frontend chat → `POST /ask` (LangGraph agent)

## 🎯 Test Flow

1. **Sign Up/In** → Creates Supabase user
2. **Write Entry** → Saves to database, generates embedding (async)
3. **View Calendar** → Loads entries from database
4. **Ask Question** → LangGraph agent retrieves and answers

## 🐛 Troubleshooting

### Frontend can't connect to backend
- Check backend is running: `curl http://localhost:8000/health`
- Verify `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local`

### Authentication errors
- Check Supabase credentials in `.env.local`
- Verify user is signed in (check browser console)

### API errors
- Check browser Network tab for error details
- Verify JWT token is being sent in headers
- Check backend logs for errors

## 📚 Documentation

- `backend/README.md` - Backend architecture
- `frontend/FRONTEND_BACKEND_INTEGRATION.md` - Integration details
- `backend/PRODUCTION_HARDENING.md` - Production features

## 🎉 You're Ready!

Both frontend and backend are now connected and ready to use!

