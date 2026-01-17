# How to Run LifeMemory AI Backend

## Quick Start

### 1. Make sure you're in the backend directory
```bash
cd backend
```

### 2. Start the server
```bash
python main.py
```

That's it! The server will start on `http://localhost:8000`

## What You'll See

When the server starts successfully, you'll see:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Production safety validation passed
INFO:     Database connection verified successfully
INFO:     LLM provider initialized: openai
INFO:     Embedding provider initialized: cohere
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Test the Server

### Option 1: Using curl (PowerShell)
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
```

### Option 2: Using curl (if installed)
```bash
curl http://localhost:8000/health
```

### Option 3: Open in Browser
Visit: http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2024-...",
  "service": "LifeMemory AI API"
}
```

## Stop the Server

Press `CTRL+C` in the terminal where the server is running.

## Running in Background (Optional)

### Windows PowerShell
```powershell
Start-Process python -ArgumentList "main.py" -NoNewWindow
```

### Or use a new terminal
Just open a new terminal window - the server will keep running in the original terminal.

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "Database connection failed"
- Check your `.env` file has the correct `DATABASE_URL`
- Make sure you've run the database schema in Supabase SQL Editor

### "Port already in use"
- Another process is using port 8000
- Change `API_PORT=8001` in `.env` and restart

### Server won't start
- Check that all required environment variables are set in `.env`
- Look at the error messages - they'll tell you what's missing

## Development Mode

For auto-reload on code changes, set in `.env`:
```
ENV=development
```

Then restart the server.

## Production Mode

For production, set in `.env`:
```
ENV=production
```

## API Endpoints

Once running, your API is available at:

- **Health Check**: `GET http://localhost:8000/health`
- **Add Journal**: `POST http://localhost:8000/journal/add` (requires auth)
- **List Journals**: `GET http://localhost:8000/journal/list` (requires auth)
- **Ask Question**: `POST http://localhost:8000/ask` (requires auth)
- **Get Insights**: `GET http://localhost:8000/insights/summary` (requires auth)

## Next Steps

1. ✅ Server is running
2. ✅ Test `/health` endpoint
3. ⏭️ Connect your frontend to `http://localhost:8000`
4. ⏭️ Use Supabase Auth to get JWT tokens for authenticated endpoints

