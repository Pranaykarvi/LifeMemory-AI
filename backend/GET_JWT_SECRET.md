# How to Get Your JWT Secret

## ⚠️ Important Note

The JWT secret is **different** from the public key you provided. The JWT secret is used to **verify** JWT tokens, while the public key is for a different purpose.

## Steps to Get JWT Secret

1. **Go to your Supabase Dashboard:**
   - https://brcfzyyvgotqvgjwqkov.supabase.co

2. **Navigate to Settings:**
   - Click on the **Settings** icon (gear) in the left sidebar
   - Or go directly to: https://brcfzyyvgotqvgjwqkov.supabase.co/project/settings/api

3. **Find JWT Settings:**
   - Scroll down to the **"JWT Settings"** section
   - Look for **"JWT Secret"**

4. **Reveal the Secret:**
   - Click the **"Reveal"** button (or eye icon) next to JWT Secret
   - Copy the entire secret string

5. **Update your .env file:**
   - Open `backend/.env`
   - Find the line: `SUPABASE_JWT_SECRET=YOUR_JWT_SECRET_HERE`
   - Replace `YOUR_JWT_SECRET_HERE` with the secret you copied

## What the JWT Secret Looks Like

The JWT secret is typically a long string that looks like:
```
your-super-secret-jwt-token-with-at-least-32-characters
```

It's **NOT** the same as:
- The anon key (JWT token)
- The service_role key (JWT token)
- The public key (JSON format)

## Alternative: Check Project Settings

If you can't find it in the API settings:
1. Go to **Project Settings** → **API**
2. Look for **"JWT Secret"** or **"JWT Settings"**
3. It might be under **"Auth"** settings instead

## Once You Have It

After updating your `.env` file with the JWT secret, you can test the application:

```bash
cd backend
python main.py
```

The application will validate all configuration on startup and tell you if anything is missing.

