# SQL Dialect Notes

**Project database:** SQLite 3.x (Python `sqlite3` stdlib)  
**Standard followed:** ANSI SQL where possible; SQLite-specific syntax noted explicitly.

---

## Why SQLite

Zero-setup, file-based, fully reproducible from a `git clone`. Supports CTEs, window functions (since v3.25, released 2018), and JSON functions. No server process needed. See `docs/decision_log.md` DEC-007.

---

## Key Differences: SQLite vs PostgreSQL vs MySQL

| Feature | SQLite | PostgreSQL | MySQL 8+ |
|---|---|---|---|
| Window functions | ✓ (v3.25+) | ✓ | ✓ |
| CTEs | ✓ | ✓ | ✓ (v8+) |
| `DATE_TRUNC()` | ✗ | ✓ | ✗ |
| `STRFTIME()` | ✓ (SQLite) | ✗ | ✗ |
| Date arithmetic | `julianday()` or `date(col, '+N days')` | `col + INTERVAL 'N days'` | `DATE_ADD(col, INTERVAL N DAY)` |
| Boolean type | Stored as INTEGER (0/1) | Native BOOLEAN | Native TINYINT(1) or BOOLEAN |
| `ILIKE` (case-insensitive LIKE) | ✗ (use `LOWER()` + `LIKE`) | ✓ | ✗ (use `LIKE` which is case-insensitive by default) |
| `GENERATE_SERIES()` | ✗ | ✓ | ✗ |
| Integer division | Returns integer | Returns integer | Returns float (use `DIV`) |
| `NULLIF()` for divide-by-zero | ✓ | ✓ | ✓ |

---

## SQLite-Specific Patterns Used in This Project

### 1. Date truncation to month
```sql
-- SQLite
STRFTIME('%Y-%m', event_date) AS year_month

-- PostgreSQL equivalent
DATE_TRUNC('month', event_date) AS year_month
```

### 2. Date arithmetic (add N days)
```sql
-- SQLite
DATE(signup_date, '+30 days')

-- PostgreSQL equivalent
signup_date + INTERVAL '30 days'

-- MySQL equivalent
DATE_ADD(signup_date, INTERVAL 30 DAY)
```

### 3. Days between two dates
```sql
-- SQLite
JULIANDAY(end_date) - JULIANDAY(start_date)

-- PostgreSQL equivalent
end_date - start_date   -- returns integer for DATE types

-- MySQL equivalent
DATEDIFF(end_date, start_date)
```

### 4. Case-insensitive string comparison
```sql
-- SQLite (no ILIKE)
WHERE LOWER(city) = 'mumbai'

-- PostgreSQL
WHERE city ILIKE 'mumbai'
```

### 5. Boolean columns
```sql
-- SQLite stores booleans as INTEGER
-- 1 = TRUE, 0 = FALSE
-- Always cast explicitly in Python:
-- df['is_churned'].astype(bool)
```

---

## Notes for Production Migration

If this project were migrated to a production PostgreSQL system:
1. Replace `STRFTIME('%Y-%m', ...)` with `DATE_TRUNC('month', ...)`.
2. Replace `JULIANDAY()` difference with simple `date2 - date1`.
3. Replace `LOWER() + LIKE` with `ILIKE`.
4. Replace date string manipulation with proper `INTERVAL` arithmetic.
5. Consider `GENERATE_SERIES()` for building date spines (calendar tables), replacing Python-generated date tables.
6. Add schema and role-based access controls (no equivalent in SQLite).
7. Use `COPY FROM` or `\copy` instead of Python `INSERT` loops for bulk loading.
