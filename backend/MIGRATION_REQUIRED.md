# ⚠️ Database Migration Required

## Error Message

If you see this error:
```
asyncpg.exceptions.UndefinedColumnError: column "entry_date" does not exist
```

This means you need to run the database migration to add the `entry_date` column.

## Quick Fix

### Step 1: Open Supabase SQL Editor

1. Go to your Supabase Dashboard: https://brcfzyyvgotqvgjwqkov.supabase.co
2. Click **SQL Editor** in the left sidebar
3. Click **New Query**

### Step 2: Run Migration Script

1. Open the file: `backend/database/migration_add_entry_date.sql`
2. Copy the **entire contents** of the file
3. Paste into the Supabase SQL Editor
4. Click **Run** (or press Ctrl+Enter)

### Step 3: Verify Migration

The migration will:
- ✅ Add `entry_date` column to `journals` table
- ✅ Add `entry_date` column to `journal_embeddings` table
- ✅ Populate `entry_date` from existing `created_at` timestamps
- ✅ Add unique constraint (one entry per user per day)
- ✅ Add indexes for performance

### Step 4: Restart Backend

After running the migration, restart your backend server:

```bash
# Stop the server (Ctrl+C)
# Then restart:
python main.py
```

## What the Migration Does

The migration script:
1. **Safely adds columns** - Uses `IF NOT EXISTS` checks
2. **Preserves existing data** - Populates `entry_date` from `created_at`
3. **Removes duplicates** - Keeps most recent entry per day
4. **Adds constraints** - Enforces one entry per user per day
5. **Adds indexes** - Improves query performance

## If Migration Fails

If you encounter errors during migration:

1. **Check for existing data conflicts:**
   - The migration removes duplicate entries automatically
   - If you have many duplicates, it may take a moment

2. **Check RLS policies:**
   - Make sure you're running as a user with proper permissions
   - Or use the service role key temporarily

3. **Manual migration:**
   - You can run each step of the migration separately
   - See `backend/database/migration_add_entry_date.sql` for individual steps

## After Migration

Once the migration is complete:
- ✅ `/journal/save` endpoint will work
- ✅ `/journal/list` endpoint will work
- ✅ `/journal/get` endpoint will work
- ✅ `/journal/days-with-entries` endpoint will work
- ✅ Calendar UI will show checkmarks correctly

## Need Help?

If you're still having issues:
1. Check the Supabase SQL Editor for any error messages
2. Verify the migration completed successfully
3. Check that both `journals` and `journal_embeddings` tables have `entry_date` column

