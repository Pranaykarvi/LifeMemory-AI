# Database Connection Issue Fix

## Problem

The server is failing to connect to the database with error:
```
socket.gaierror: [Errno 11001] getaddrinfo failed
```

This means the database hostname cannot be resolved.

## Solution

Your DATABASE_URL in `.env` should use the **pooler** connection, not the direct connection.

### Current (may not work):
```
DATABASE_URL=postgresql://postgres:MuKaMbIkA2005@db.brcfzyyvgotqvgjwqkov.supabase.co:5432/postgres
```

### Try this instead (pooler connection):
```
DATABASE_URL=postgresql://postgres.brcfzyyvgotqvgjwqkov:MuKaMbIkA2005@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

Or use the **transaction mode** pooler:
```
DATABASE_URL=postgresql://postgres.brcfzyyvgotqvgjwqkov:MuKaMbIkA2005@aws-0-us-east-1.pooler.supabase.com:5432/postgres?pgbouncer=true
```

## How to Get the Correct Connection String

1. Go to your Supabase Dashboard: https://brcfzyyvgotqvgjwqkov.supabase.co
2. Navigate to **Settings** → **Database**
3. Scroll to **"Connection string"** section
4. Select **"Session mode"** or **"Transaction mode"**
5. Copy the connection string
6. Replace `[YOUR-PASSWORD]` with your actual password: `MuKaMbIkA2005`

## Update Your .env File

Update the `DATABASE_URL` line in your `.env` file with the correct connection string from Supabase dashboard.

## Test Connection

After updating, restart the server:
```bash
python main.py
```

The server should now connect to the database successfully.

