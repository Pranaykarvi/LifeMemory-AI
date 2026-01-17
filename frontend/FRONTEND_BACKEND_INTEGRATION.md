# Frontend-Backend Integration Guide

## ✅ What's Been Connected

### 1. Authentication
- **Frontend**: Uses Supabase Auth client
- **Backend**: Verifies Supabase JWT tokens
- **Flow**: User signs in → Gets JWT token → Token sent to backend in Authorization header

### 2. Journal Management
- **Create Entry**: `POST /journal/add` - Saves journal entries with mood
- **List Entries**: `GET /journal/list` - Loads entries for calendar and sidebar
- **Auto-refresh**: Sidebar updates when new entries are saved

### 3. Memory Chat
- **Ask Questions**: `POST /ask` - Uses LangGraph agent to answer questions
- **Real-time**: Connects to backend API with authentication

## 📁 Files Created/Updated

### New Files
- `frontend/lib/supabase.ts` - Supabase client and auth functions
- `frontend/lib/api.ts` - API client for backend communication
- `frontend/.env.local` - Environment variables (gitignored)
- `frontend/.env.local.example` - Example environment file

### Updated Files
- `frontend/components/auth-page.tsx` - Real Supabase authentication
- `frontend/components/journal-editor.tsx` - Saves to backend API
- `frontend/components/journal-sidebar.tsx` - Loads from backend API
- `frontend/components/memory-chat.tsx` - Uses backend /ask endpoint
- `frontend/app/page.tsx` - Auth state management
- `frontend/package.json` - Added @supabase/supabase-js
- `backend/main.py` - Updated CORS for Next.js

## 🚀 Setup Instructions

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

This will install `@supabase/supabase-js` and other dependencies.

### 2. Environment Variables

The `.env.local` file has been created with your credentials. If you need to recreate it:

```bash
# In frontend directory
NEXT_PUBLIC_SUPABASE_URL=https://brcfzyyvgotqvgjwqkov.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Backend

```bash
cd backend
python main.py
```

Backend should be running on `http://localhost:8000`

### 4. Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will run on `http://localhost:3000`

## 🔄 How It Works

### Authentication Flow
1. User enters email/password in frontend
2. Frontend calls `signIn()` or `signUp()` from `lib/supabase.ts`
3. Supabase returns JWT token
4. Token stored in Supabase client session
5. All API calls include token in `Authorization: Bearer <token>` header
6. Backend verifies token and extracts `user_id`

### Journal Entry Flow
1. User writes entry in `JournalEditor`
2. Clicks "Save Entry"
3. Frontend calls `journalApi.create()` from `lib/api.ts`
4. API client gets JWT token and sends POST to `/journal/add`
5. Backend saves entry and generates embedding (async)
6. Frontend refreshes sidebar to show new entry

### Memory Chat Flow
1. User asks question in `MemoryChat`
2. Frontend calls `memoryApi.ask()` from `lib/api.ts`
3. API client sends POST to `/ask` with JWT token
4. Backend LangGraph agent processes query
5. Returns evidence-based answer
6. Frontend displays answer in chat

## 🔒 Security

- **JWT Verification**: Every backend request verifies JWT token
- **User Isolation**: All queries filter by `user_id` from token
- **RLS Policies**: Database-level security enforced
- **CORS**: Backend allows requests from `http://localhost:3000`

## 🐛 Troubleshooting

### "Not authenticated" error
- Check that user is signed in
- Verify JWT token is being sent in headers
- Check Supabase auth session

### CORS errors
- Make sure backend CORS includes `http://localhost:3000`
- Check `NEXT_PUBLIC_API_URL` is correct

### API connection failed
- Verify backend is running on `http://localhost:8000`
- Check `/health` endpoint works
- Verify `.env.local` has correct `NEXT_PUBLIC_API_URL`

### Database errors
- Make sure database schema is run in Supabase
- Check backend can connect to database
- Verify RLS policies are set up

## 📝 Next Steps

1. **Test the full flow**:
   - Sign up/Sign in
   - Create journal entry
   - Ask a question about your entry

2. **Optional Enhancements**:
   - Add error toast notifications
   - Add loading states
   - Add entry editing
   - Add entry deletion
   - Add insights dashboard

## 🎯 API Endpoints Used

- `POST /journal/add` - Create journal entry
- `GET /journal/list` - List journal entries
- `POST /ask` - Ask memory question
- `GET /health` - Health check (no auth)

All endpoints (except `/health`) require:
```
Authorization: Bearer <jwt-token>
```

