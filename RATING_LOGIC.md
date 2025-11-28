# Рейтинг беті логикасы / Rating Page Logic

## Қазақша түсіндірме

### Жалпы шолу

Рейтинг беті (`/rating`) барлық қолданушылардың жалпы ұпай бойынша сұрыпталған тізімін көрсетеді.

### Деректер ағыны

```
┌─────────────────┐     GET /api/rating?limit=20     ┌─────────────────┐
│  Rating Page    │  ─────────────────────────────▶  │   FastAPI API   │
│  (Next.js)      │                                   │   (main.py)     │
└─────────────────┘                                   └────────┬────────┘
                                                              │
                                                              │ get_top_users()
                                                              ▼
                                                      ┌─────────────────┐
                                                      │   database.py   │
                                                      │   (SQLite)      │
                                                      └─────────────────┘
```

### Рейтинг есептеу логикасы

1. **Қолданушылар біріктіру**: Telegram және веб қолданушылар UNION арқылы біріктіріледі
2. **Сұрыптау**: `points DESC, solved_count DESC` - алдымен ұпай, содан кейін шешілген есептер саны
3. **Веб қолданушылар фильтрі**: Тек nickname орнатқан веб қолданушылар көрсетіледі

### SQL сұранымы

```sql
-- First part: All Telegram users (no filtering)
SELECT user_id, username, full_name, NULL as email, NULL as name, NULL as nickname,
       points, solved_count, 'telegram' as source
FROM users

UNION ALL

-- Second part: Only Web users WITH a nickname set (privacy filter)
SELECT NULL as user_id, NULL as username, NULL as full_name, 
       email, name, nickname, points, solved_count, 'web' as source
FROM web_users
WHERE nickname IS NOT NULL AND nickname != ''

-- Final sorting and limiting applied to combined result
ORDER BY points DESC, solved_count DESC
LIMIT ?
```

**Ескерту**: `WHERE` шарты тек `web_users` кестесіне қолданылады, `users` кестесінде барлық қолданушылар қосылады.

### Медаль жүйесі (Frontend)

| Орын | Медаль |
|------|--------|
| 1    | 🥇     |
| 2    | 🥈     |
| 3    | 🥉     |
| 4+   | Сан    |

### Ұпай жинау жолдары

- Есепті **дұрыс шешу** = +1 ұпай
- Әр есепті тек **бір рет** шешуге болады
- Қате жауап ұпай бермейді

---

## English explanation

### Overview

The rating page (`/rating`) displays a leaderboard of all users sorted by total points earned.

### Data Flow

1. **Frontend** (`web/app/rating/page.tsx`): Makes a GET request to `/api/rating?limit=20`
2. **Backend** (`bot/main.py`): The `/api/rating` endpoint calls `db.get_top_users(limit)`
3. **Database** (`bot/database.py`): Executes a UNION query combining Telegram and Web users

### Rating Calculation Logic

The `get_top_users()` function in `database.py`:

1. **Combines users**: Uses UNION ALL to merge Telegram users (`users` table) and Web users (`web_users` table)
2. **Sorting**: Primary sort by `points DESC`, secondary by `solved_count DESC`
3. **Web user filter**: Only web users with a non-empty nickname are included in the rating

### Key Points

| Feature | Description |
|---------|-------------|
| **Score basis** | Total all-time points (not weekly) |
| **User sources** | Both Telegram and Web users |
| **Privacy** | Web users need a nickname to appear publicly |
| **Limit** | Default shows top 20 users |

### How Points Are Earned

- Correctly solving a task = **+1 point**
- Each task can only be solved **once** per user
- Incorrect answers do not award points

### Difference from League Ranking

| Рейтинг (Rating) | Лига (League) |
|------------------|---------------|
| All-time total points | Weekly points only |
| All users combined | Users grouped by league level |
| No promotion/demotion | Top 7 promoted, bottom 5 demoted |

---

## Код мысалдары / Code Examples

### Frontend - Fetching Rating

```typescript
// web/app/rating/page.tsx
const fetchRating = async () => {
  try {
    const res = await fetch(`${apiUrl}/api/rating?limit=20`);
    if (!res.ok) {
      throw new Error(`Server error: ${res.status}`);
    }
    const data = await res.json();
    setUsers(data.users || []);
  } catch (err) {
    setError(err instanceof Error ? err.message : "Error occurred");
  }
};
```

### Backend - API Endpoint

```python
# bot/main.py
@app.get("/api/rating")
async def get_rating(limit: int = 10):
    """Get top users leaderboard
    
    Args:
        limit: Number of users to return (default: 10, frontend uses 20)
    """
    users = await db.get_top_users(limit)
    return {"users": users}
```

### Database - Query Function

```python
# bot/database.py
async def get_top_users(limit: int = 10) -> List[Dict[str, Any]]:
    """Telegram және веб қолданушыларының рейтингі
    
    Combines both Telegram and Web users using UNION ALL,
    sorts by points DESC then solved_count DESC.
    Web users must have a nickname to be included.
    """
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        # Execute UNION query (see SQL query section above)
        async with conn.execute("...", (limit,)) as cur:
            return [dict(row) for row in await cur.fetchall()]
```
