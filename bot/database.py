# bot/database.py
import aiosqlite
from typing import Dict, Any, List, Optional

DB_NAME = "database.db"
MAX_NICKNAME_LENGTH = 30


async def init_db() -> None:
    """Базаны құрып, миграцияларды орындайды"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row

        # WAL режимі – жылдам әрі қауіпсіз
        await conn.execute("PRAGMA journal_mode = WAL;")
        await conn.execute("PRAGMA synchronous = NORMAL;")
        await conn.execute("PRAGMA foreign_keys = ON;")

        # Таблицалар
        await conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                points INTEGER DEFAULT 0,
                solved_count INTEGER DEFAULT 0,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS web_users (
                email TEXT PRIMARY KEY,
                name TEXT,
                google_id TEXT,
                points INTEGER DEFAULT 0,
                solved_count INTEGER DEFAULT 0,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                correct_option TEXT NOT NULL,
                solution_image_path TEXT,
                answer_type TEXT DEFAULT 'quiz',
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_solutions (
                user_id INTEGER,
                task_id INTEGER,
                is_correct BOOLEAN,
                attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, task_id)
            );

            CREATE TABLE IF NOT EXISTS web_user_solutions (
                email TEXT,
                task_id INTEGER,
                is_correct BOOLEAN,
                attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (email, task_id)
            );
        """)

        # Миграциялар (ескі базаларға) - MUST BE BEFORE INDEXES
        migrations = [
            "ALTER TABLE tasks ADD COLUMN solution_image_path TEXT",
            "ALTER TABLE tasks ADD COLUMN answer_type TEXT DEFAULT 'quiz'",
            "ALTER TABLE users ADD COLUMN full_name TEXT",
            "ALTER TABLE tasks ADD COLUMN created_by INTEGER",
            "ALTER TABLE web_users ADD COLUMN nickname TEXT",
            "ALTER TABLE users ADD COLUMN league TEXT DEFAULT 'bronze'",
            "ALTER TABLE users ADD COLUMN weekly_points INTEGER DEFAULT 0",
            "ALTER TABLE web_users ADD COLUMN league TEXT DEFAULT 'bronze'",
            "ALTER TABLE web_users ADD COLUMN weekly_points INTEGER DEFAULT 0"
        ]
        for sql in migrations:
            try:
                await conn.execute(sql)
            except aiosqlite.OperationalError:
                pass  # колонка бар деген

        # Индекстер – жылдамдық үшін өте маңызды!
        await conn.executescript("""
            CREATE INDEX IF NOT EXISTS idx_us_user ON user_solutions(user_id);
            CREATE INDEX IF NOT EXISTS idx_us_task ON user_solutions(task_id);
            CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at);
            CREATE INDEX IF NOT EXISTS idx_wus_email ON web_user_solutions(email);
            CREATE INDEX IF NOT EXISTS idx_wus_task ON web_user_solutions(task_id);
            CREATE INDEX IF NOT EXISTS idx_users_league ON users(league);
            CREATE INDEX IF NOT EXISTS idx_users_weekly_points ON users(weekly_points DESC);
            CREATE INDEX IF NOT EXISTS idx_web_users_league ON web_users(league);
            CREATE INDEX IF NOT EXISTS idx_web_users_weekly_points ON web_users(weekly_points DESC);
            CREATE INDEX IF NOT EXISTS idx_users_points ON users(points DESC);
            CREATE INDEX IF NOT EXISTS idx_web_users_points ON web_users(points DESC);
        """)

        await conn.commit()


# ==================== ПАЙДАЛАНУШЫЛАР ====================
async def ensure_user(user_id: int, username: Optional[str], full_name: str) -> None:
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        username = username if username and username != "None" else None
        full_name = full_name or "Қолданушы"

        # Use INSERT ... ON CONFLICT to handle race conditions atomically
        await conn.execute(
            """INSERT INTO users (user_id, username, full_name) VALUES (?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET username = excluded.username, full_name = excluded.full_name""",
            (user_id, username, full_name)
        )
        await conn.commit()


async def get_user_stats(user_id: int) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_all_users() -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("SELECT * FROM users ORDER BY points DESC") as cur:
            return [dict(row) for row in await cur.fetchall()]


# ==================== WEB ПАЙДАЛАНУШЫЛАР ====================
async def ensure_web_user(email: str, name: str, google_id: str) -> None:
    """Веб қолданушыны қосу немесе жаңарту"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        
        # Use INSERT ... ON CONFLICT to handle race conditions atomically
        await conn.execute(
            """INSERT INTO web_users (email, name, google_id) VALUES (?, ?, ?)
               ON CONFLICT(email) DO UPDATE SET name = excluded.name, google_id = excluded.google_id""",
            (email, name, google_id)
        )
        await conn.commit()


async def get_web_user_stats(email: str) -> Optional[Dict[str, Any]]:
    """Веб қолданушының статистикасын алу"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("SELECT * FROM web_users WHERE email = ?", (email,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def update_web_user_nickname(email: str, nickname: str) -> None:
    """Веб қолданушының никнеймін жаңарту"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        # Validate and clean nickname
        cleaned_nickname = nickname.strip() if nickname else None
        if cleaned_nickname and len(cleaned_nickname) > MAX_NICKNAME_LENGTH:
            raise ValueError(f"Никнейм {MAX_NICKNAME_LENGTH} таңбадан аспауы керек")
        
        await conn.execute(
            "UPDATE web_users SET nickname = ? WHERE email = ?",
            (cleaned_nickname, email)
        )
        await conn.commit()


async def get_top_users(limit: int = 10) -> List[Dict[str, Any]]:
    """Telegram және веб қолданушыларының рейтингі"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        
        # UNION query to combine both user types and sort in database
        # Web users must have a nickname to appear in rating
        async with conn.execute(
            """
            SELECT user_id, username, full_name, NULL as email, NULL as name, NULL as nickname,
                   points, solved_count, 'telegram' as source
            FROM users
            UNION ALL
            SELECT NULL as user_id, NULL as username, NULL as full_name, 
                   email, name, nickname, points, solved_count, 'web' as source
            FROM web_users
            WHERE nickname IS NOT NULL AND nickname != ''
            ORDER BY points DESC, solved_count DESC
            LIMIT ?
            """, (limit,)
        ) as cur:
            return [dict(row) for row in await cur.fetchall()]


# ==================== ЕСЕПТЕР ====================
async def add_task(
        image_path: str,
        correct_option: str,
        solution_image_path: str,
        answer_type: str,
        created_by: int
) -> int:
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            """INSERT INTO tasks 
               (image_path, correct_option, solution_image_path, answer_type, created_by)
               VALUES (?, ?, ?, ?, ?)""",
            (image_path, correct_option, solution_image_path, answer_type, created_by)
        )
        await conn.commit()
        return cursor.lastrowid


async def get_task(task_id: int) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def list_tasks(limit: int = 200) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("SELECT * FROM tasks ORDER BY id DESC LIMIT ?", (limit,)) as cur:
            return [dict(row) for row in await cur.fetchall()]


async def get_random_unsolved_task(user_id: int) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("""
            SELECT t.* FROM tasks t
            LEFT JOIN user_solutions us ON t.id = us.task_id AND us.user_id = ?
            WHERE us.task_id IS NULL
            ORDER BY RANDOM() LIMIT 1
        """, (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def has_solved(user_id: int, task_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        async with conn.execute(
                "SELECT 1 FROM user_solutions WHERE user_id = ? AND task_id = ?",
                (user_id, task_id)
        ) as cur:
            return await cur.fetchone() is not None


async def delete_task(task_id: int) -> None:
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        await conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        await conn.execute("DELETE FROM user_solutions WHERE task_id = ?", (task_id,))
        await conn.commit()


async def update_task_image_path(task_id: int, new_path: str) -> None:
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        await conn.execute("UPDATE tasks SET image_path = ? WHERE id = ?", (new_path, task_id))
        await conn.commit()


async def update_task_solution_image_path(task_id: int, new_path: str) -> None:
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        await conn.execute("UPDATE tasks SET solution_image_path = ? WHERE id = ?", (new_path, task_id))
        await conn.commit()


async def update_task_image_path_only(task_id: int, new_path: str) -> None:
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        await conn.execute("UPDATE tasks SET image_path = ? WHERE id = ?", (new_path, task_id))
        await conn.commit()


async def update_task_correct_option(task_id: int, new_option: str) -> None:
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        await conn.execute("UPDATE tasks SET correct_option = ? WHERE id = ?", (new_option, task_id))
        await conn.commit()


# ==================== ШЕШІМДЕР ====================
async def mark_attempted(user_id: int, task_id: int) -> None:
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        await conn.execute(
            "INSERT OR IGNORE INTO user_solutions (user_id, task_id, is_correct) VALUES (?, ?, 0)",
            (user_id, task_id)
        )
        await conn.commit()


# ==================== WEB ШЕШІМДЕР ====================
async def mark_web_attempted(email: str, task_id: int) -> None:
    """Веб қолданушы есепті қате шешкен кезде"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        await conn.execute(
            "INSERT OR IGNORE INTO web_user_solutions (email, task_id, is_correct) VALUES (?, ?, 0)",
            (email, task_id)
        )
        await conn.commit()


async def has_web_solved(email: str, task_id: int) -> bool:
    """Веб қолданушы есепті бұрын шешкен бе"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        async with conn.execute(
                "SELECT 1 FROM web_user_solutions WHERE email = ? AND task_id = ?",
                (email, task_id)
        ) as cur:
            return await cur.fetchone() is not None


async def get_random_unsolved_task_web(email: str) -> Optional[Dict[str, Any]]:
    """Веб қолданушы үшін шешілмеген кездейсоқ есепті алу"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("""
            SELECT t.* FROM tasks t
            LEFT JOIN web_user_solutions wus ON t.id = wus.task_id AND wus.email = ?
            WHERE wus.task_id IS NULL
            ORDER BY RANDOM() LIMIT 1
        """, (email,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_bot_statistics() -> Dict[str, int]:
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        stats = {}
        queries = {
            "total_users": "SELECT COUNT(*) FROM users",
            "total_tasks": "SELECT COUNT(*) FROM tasks",
            "total_solutions": "SELECT COUNT(*) FROM user_solutions",
            "new_users_today": "SELECT COUNT(*) FROM users WHERE DATE(registration_date) = DATE('now')"
        }
        for key, sql in queries.items():
            async with conn.execute(sql) as cur:
                stats[key] = (await cur.fetchone())[0]
        return stats


# ==================== ЛИГА ЖҮЙЕСІ ====================

# Лига деңгейлері (Duolingo стилінде)
LEAGUES = ["bronze", "silver", "gold", "platinum", "diamond"]
LEAGUE_NAMES = {
    "bronze": "🥉 Қола",
    "silver": "🥈 Күміс", 
    "gold": "🥇 Алтын",
    "platinum": "💎 Платина",
    "diamond": "💠 Алмас"
}

# Лигаға көтерілу/түсу үшін қажетті орын
PROMOTION_THRESHOLD = 3  # Топ 3 көтеріледі
DEMOTION_THRESHOLD = 3   # Соңғы 3 түседі


def get_league_index(league: str) -> int:
    """Лига индексін алу"""
    try:
        return LEAGUES.index(league.lower())
    except ValueError:
        return 0  # bronze по умолчанию


async def mark_solved_and_add_point(user_id: int, task_id: int) -> None:
    """Telegram қолданушы есепті шешіп ұпай алады (жалпы және апта)"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        await conn.execute(
            "INSERT OR REPLACE INTO user_solutions (user_id, task_id, is_correct) VALUES (?, ?, 1)",
            (user_id, task_id)
        )
        await conn.execute(
            "UPDATE users SET points = points + 1, solved_count = solved_count + 1, weekly_points = weekly_points + 1 WHERE user_id = ?",
            (user_id,)
        )
        await conn.commit()


async def mark_web_solved_and_add_point(email: str, task_id: int) -> None:
    """Веб қолданушы есепті дұрыс шешкен кезде (жалпы және апта)"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        await conn.execute(
            "INSERT OR REPLACE INTO web_user_solutions (email, task_id, is_correct) VALUES (?, ?, 1)",
            (email, task_id)
        )
        await conn.execute(
            "UPDATE web_users SET points = points + 1, solved_count = solved_count + 1, weekly_points = weekly_points + 1 WHERE email = ?",
            (email,)
        )
        await conn.commit()


async def get_league_leaderboard(league: str, limit: int = 30) -> List[Dict[str, Any]]:
    """Белгілі бір лиганың рейтингін алу (апталық ұпай бойынша)"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        
        async with conn.execute(
            """
            SELECT user_id, username, full_name, NULL as email, NULL as name, NULL as nickname,
                   points, solved_count, weekly_points, league, 'telegram' as source
            FROM users
            WHERE league = ?
            UNION ALL
            SELECT NULL as user_id, NULL as username, NULL as full_name, 
                   email, name, nickname, points, solved_count, weekly_points, league, 'web' as source
            FROM web_users
            WHERE league = ? AND nickname IS NOT NULL AND nickname != ''
            ORDER BY weekly_points DESC, points DESC
            LIMIT ?
            """, (league, league, limit)
        ) as cur:
            return [dict(row) for row in await cur.fetchall()]


async def get_user_league_info(user_id: int) -> Optional[Dict[str, Any]]:
    """Telegram қолданушының лига ақпаратын алу"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            "SELECT league, weekly_points, points FROM users WHERE user_id = ?", 
            (user_id,)
        ) as cur:
            row = await cur.fetchone()
            if not row:
                return None
            
            result = dict(row)
            
            # Лигадағы орынды табу (SQL COUNT арқылы - өте жылдам)
            # Count users in same league with higher weekly_points, or same points but higher total points
            async with conn.execute(
                """
                SELECT COUNT(*) + 1 as rank FROM (
                    SELECT weekly_points, points FROM users 
                    WHERE league = ? AND user_id != ?
                    UNION ALL
                    SELECT weekly_points, points FROM web_users 
                    WHERE league = ? AND nickname IS NOT NULL AND nickname != ''
                )
                WHERE weekly_points > ? OR (weekly_points = ? AND points > ?)
                """,
                (result['league'], user_id, result['league'], 
                 result['weekly_points'], result['weekly_points'], result['points'])
            ) as cur:
                rank_row = await cur.fetchone()
                result['rank'] = rank_row[0] if rank_row else 1
            
            return result


async def get_web_user_league_info(email: str) -> Optional[Dict[str, Any]]:
    """Веб қолданушының лига ақпаратын алу"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            "SELECT league, weekly_points, points FROM web_users WHERE email = ?", 
            (email,)
        ) as cur:
            row = await cur.fetchone()
            if not row:
                return None
            
            result = dict(row)
            
            # Лигадағы орынды табу (SQL COUNT арқылы - өте жылдам)
            # Count users in same league with higher weekly_points, or same points but higher total points
            async with conn.execute(
                """
                SELECT COUNT(*) + 1 as rank FROM (
                    SELECT weekly_points, points FROM users 
                    WHERE league = ?
                    UNION ALL
                    SELECT weekly_points, points FROM web_users 
                    WHERE league = ? AND email != ? AND nickname IS NOT NULL AND nickname != ''
                )
                WHERE weekly_points > ? OR (weekly_points = ? AND points > ?)
                """,
                (result['league'], result['league'], email,
                 result['weekly_points'], result['weekly_points'], result['points'])
            ) as cur:
                rank_row = await cur.fetchone()
                result['rank'] = rank_row[0] if rank_row else 1
            
            return result


async def reset_weekly_points() -> None:
    """Апталық ұпайларды нөлге тастау және лигаларды жаңарту"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        
        # Әр лига үшін көтерілу/түсу
        for i, league in enumerate(LEAGUES):
            leaderboard = await get_league_leaderboard(league, limit=100)
            
            # Топ 3 - көтеріледі (соңғы лигадан басқа)
            if i < len(LEAGUES) - 1:
                next_league = LEAGUES[i + 1]
                for j in range(min(PROMOTION_THRESHOLD, len(leaderboard))):
                    user = leaderboard[j]
                    if user['source'] == 'telegram':
                        await conn.execute(
                            "UPDATE users SET league = ? WHERE user_id = ?",
                            (next_league, user['user_id'])
                        )
                    else:
                        await conn.execute(
                            "UPDATE web_users SET league = ? WHERE email = ?",
                            (next_league, user['email'])
                        )
            
            # Соңғы 3 - түседі (бірінші лигадан басқа)
            # Demotion only if there are enough users (more than promotion + demotion zones)
            min_users_for_demotion = PROMOTION_THRESHOLD + DEMOTION_THRESHOLD + 1
            if i > 0 and len(leaderboard) >= min_users_for_demotion:
                prev_league = LEAGUES[i - 1]
                for j in range(max(0, len(leaderboard) - DEMOTION_THRESHOLD), len(leaderboard)):
                    user = leaderboard[j]
                    if user['source'] == 'telegram':
                        await conn.execute(
                            "UPDATE users SET league = ? WHERE user_id = ?",
                            (prev_league, user['user_id'])
                        )
                    else:
                        await conn.execute(
                            "UPDATE web_users SET league = ? WHERE email = ?",
                            (prev_league, user['email'])
                        )
        
        # Барлық апталық ұпайларды нөлге тастау
        await conn.execute("UPDATE users SET weekly_points = 0")
        await conn.execute("UPDATE web_users SET weekly_points = 0")
        await conn.commit()