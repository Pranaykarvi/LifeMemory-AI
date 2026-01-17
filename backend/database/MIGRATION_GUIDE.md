# Migration Guide: Single-Entry-Per-Day Journaling

This guide explains how to migrate from the old journaling model to the new single-entry-per-day model.

## Overview

The new model enforces:
- **One journal entry per user per calendar day**
- **Editable entries** (editing replaces the old entry)
- **Automatic embedding replacement** (old embeddings deleted when entry is edited)
- **Calendar integration** (checkmarks show days with entries)

## Migration Steps

### 1. Run the Migration SQL

Run `migration_add_entry_date.sql` in your Supabase SQL editor:

```sql
-- This will:
-- 1. Add entry_date column to journals and journal_embeddings
-- 2. Populate entry_date from existing created_at timestamps
-- 3. Add UNIQUE constraint (user_id, entry_date)
-- 4. Remove duplicate entries (keeps most recent)
-- 5. Add indexes for performance
```

### 2. Update Your Application Code

The API endpoints have changed:

**Old:** `POST /journal/add` (creates new entry)
**New:** `POST /journal/save` (UPSERT - creates or updates)

**New Endpoints:**
- `POST /journal/save` - Save/update journal entry for a date
- `GET /journal/get?entry_date=YYYY-MM-DD` - Get entry for specific date
- `GET /journal/days-with-entries?month=YYYY-MM` - Get all dates with entries (for calendar)

### 3. Frontend Changes Required

1. **Update save endpoint:**
   - Change from `/journal/add` to `/journal/save`
   - Include `entry_date` in request (YYYY-MM-DD format)

2. **Calendar integration:**
   - Call `GET /journal/days-with-entries?month=YYYY-MM`
   - Show checkmark (✓) for dates in the response

3. **Load entry for date:**
   - Call `GET /journal/get?entry_date=YYYY-MM-DD`
   - Pre-populate editor with existing content

## Database Schema Changes

### Before
```sql
CREATE TABLE journals (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    content TEXT NOT NULL,
    mood TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
```

### After
```sql
CREATE TABLE journals (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    entry_date DATE NOT NULL,  -- NEW
    content TEXT NOT NULL,
    mood TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    UNIQUE (user_id, entry_date)  -- NEW: Enforces one per day
);
```

## API Changes

### Save Journal Entry

**Request:**
```json
POST /journal/save
{
    "content": "Today I felt...",
    "mood": "happy",
    "entry_date": "2026-01-17"  // Optional, defaults to today
}
```

**Response:**
```json
{
    "id": "uuid",
    "user_id": "uuid",
    "entry_date": "2026-01-17",
    "content": "Today I felt...",
    "mood": "happy",
    "created_at": "2026-01-17T10:00:00Z",
    "updated_at": "2026-01-17T10:00:00Z"
}
```

### Get Days with Entries (Calendar)

**Request:**
```
GET /journal/days-with-entries?month=2026-01
```

**Response:**
```json
{
    "dates": ["2026-01-15", "2026-01-17", "2026-01-20"]
}
```

## Behavior Changes

1. **Editing an entry:**
   - Old: Created a new entry
   - New: Replaces the existing entry for that date
   - Old embeddings are automatically deleted
   - New embeddings are generated

2. **Multiple entries per day:**
   - Old: Allowed
   - New: Only one entry per day (enforced by database)

3. **Retrieval:**
   - Only uses `journal_embeddings` table (ensures latest embeddings)
   - Filters by `entry_date` instead of `created_at`

## Rollback (If Needed)

If you need to rollback:

1. Remove the unique constraint:
```sql
ALTER TABLE journals DROP CONSTRAINT IF EXISTS journals_user_id_entry_date_key;
```

2. Make entry_date nullable:
```sql
ALTER TABLE journals ALTER COLUMN entry_date DROP NOT NULL;
ALTER TABLE journal_embeddings ALTER COLUMN entry_date DROP NOT NULL;
```

3. Revert API code to use `/journal/add`

## Testing Checklist

- [ ] Run migration SQL successfully
- [ ] Save new journal entry for today
- [ ] Edit existing entry (should replace, not create new)
- [ ] Verify old embeddings are deleted on edit
- [ ] Verify new embeddings are created on edit
- [ ] Test calendar endpoint returns correct dates
- [ ] Test retrieval uses latest embeddings only
- [ ] Verify RLS policies still work correctly

