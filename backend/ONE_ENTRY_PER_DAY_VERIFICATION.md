# One Entry Per Day - Implementation Verification

## ✅ Database Enforcement

### Journals Table
- ✅ `UNIQUE (user_id, entry_date)` constraint enforced
- ✅ Prevents multiple entries per user per day at database level
- ✅ ON CONFLICT DO UPDATE replaces content (not append)

### Journal Embeddings Table
- ✅ `UNIQUE (user_id, entry_date)` constraint enforced
- ✅ `UNIQUE (journal_id)` constraint enforced
- ✅ Double protection against duplicate embeddings

## ✅ API Behavior

### POST /journal/save
- ✅ Uses UPSERT with `ON CONFLICT (user_id, entry_date) DO UPDATE`
- ✅ Replaces content, mood, and updated_at
- ✅ Deletes old embeddings BEFORE journal UPSERT
- ✅ Deletes by (user_id, entry_date) to catch all cases
- ✅ Generates new embedding in background task
- ✅ Background task also deletes by (user_id, entry_date) for safety

### Embedding Generation
- ✅ Deletes ALL embeddings for (user_id, entry_date) before insert
- ✅ Ensures only one embedding exists per user per day
- ✅ Works even if journal_id changes on update

## ✅ Data Consistency Guarantees

1. **Journals:**
   - Database constraint: `UNIQUE (user_id, entry_date)`
   - API logic: `ON CONFLICT DO UPDATE` (replace, not append)
   - Result: **0 or 1 journal row per (user_id, date)**

2. **Embeddings:**
   - Database constraint: `UNIQUE (user_id, entry_date)`
   - API logic: Delete before insert (by user_id + entry_date)
   - Background task: Delete before insert (by user_id + entry_date)
   - Result: **0 or 1 embedding per (user_id, date)**

## ✅ Edit-in-Place Behavior

When user saves on the same day:
1. Old embeddings deleted (by user_id + entry_date)
2. Journal entry updated (ON CONFLICT DO UPDATE)
3. New embedding generated in background
4. New embedding inserted (replaces old one)

**Result:** Content is replaced, not appended. Old data is removed.

## ✅ Calendar Integration

### GET /journal/days-with-entries?month=YYYY-MM
- ✅ Returns list of dates with entries
- ✅ Frontend can show ✓ tick for each date
- ✅ Tick appears when entry exists
- ✅ Tick disappears only if entry is deleted

## ✅ Retrieval Behavior

- ✅ Retrieval uses `journal_embeddings` table (source of truth)
- ✅ Filters by `entry_date` for temporal queries
- ✅ Only latest embeddings are used (old ones deleted)
- ✅ No historical embeddings leak into results

## 🚫 What We DON'T Do

- ❌ No `/journal/add` endpoint (removed)
- ❌ No appending to entries
- ❌ No keeping old embeddings
- ❌ No multiple entries per day
- ❌ No legacy routes exposed

## 🧪 Testing Checklist

- [ ] Save entry for today → creates new entry
- [ ] Save again for today → updates existing entry (same ID or new ID)
- [ ] Verify only one journal row exists for that date
- [ ] Verify only one embedding exists for that date
- [ ] Edit entry → old embedding deleted, new one created
- [ ] Calendar shows ✓ for dates with entries
- [ ] Retrieval uses latest embedding only
- [ ] No duplicate entries in database
- [ ] No orphaned embeddings

## 📝 Migration Required

If you see errors about missing `entry_date` column:
1. Run `backend/database/migration_add_entry_date.sql` in Supabase SQL Editor
2. This adds the column and enforces constraints
3. Restart backend after migration

