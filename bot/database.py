# bot/database.py
import aiosqlite
from typing import Dict, Any, List, Optional

DB_NAME = "database.db"
MAX_NICKNAME_LENGTH = 30
GROUP_MIN_SIZE = 30  # Minimum users in a group before creating new one
GROUP_MAX_SIZE = 30  # Maximum users in a group


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
            
            CREATE TABLE IF NOT EXISTS league_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league TEXT NOT NULL,
                week_start DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(league, week_start, id)
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

            CREATE TABLE IF NOT EXISTS web_user_achievements (
                email TEXT,
                achievement_id TEXT,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (email, achievement_id)
            );
        """)

        # Индекстер – жылдамдық үшін өте маңызды!
        # Note: Indexes on league_group_id columns (idx_users_group, idx_web_users_group) are created after migrations below
        await conn.executescript("""
            CREATE INDEX IF NOT EXISTS idx_us_user ON user_solutions(user_id);
            CREATE INDEX IF NOT EXISTS idx_us_task ON user_solutions(task_id);
            CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at);
            CREATE INDEX IF NOT EXISTS idx_wus_email ON web_user_solutions(email);
            CREATE INDEX IF NOT EXISTS idx_wus_task ON web_user_solutions(task_id);
            CREATE INDEX IF NOT EXISTS idx_league_groups ON league_groups(league, week_start);
            CREATE INDEX IF NOT EXISTS idx_wua_email ON web_user_achievements(email);
        """)

        # Миграциялар (ескі базаларға)
        migrations = [
            "ALTER TABLE tasks ADD COLUMN solution_image_path TEXT",
            "ALTER TABLE tasks ADD COLUMN answer_type TEXT DEFAULT 'quiz'",
            "ALTER TABLE users ADD COLUMN full_name TEXT",
            "ALTER TABLE tasks ADD COLUMN created_by INTEGER",
            "ALTER TABLE web_users ADD COLUMN nickname TEXT",
            "ALTER TABLE users ADD COLUMN league TEXT DEFAULT 'bronze'",
            "ALTER TABLE users ADD COLUMN weekly_points INTEGER DEFAULT 0",
            "ALTER TABLE web_users ADD COLUMN league TEXT DEFAULT 'bronze'",
            "ALTER TABLE web_users ADD COLUMN weekly_points INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN league_group_id INTEGER",
            "ALTER TABLE web_users ADD COLUMN league_group_id INTEGER"
        ]
        for sql in migrations:
            try:
                await conn.execute(sql)
            except aiosqlite.OperationalError:
                pass  # колонка бар деген

        # Create indexes on league_group_id after migrations to ensure columns exist
        await conn.executescript("""
            CREATE INDEX IF NOT EXISTS idx_users_group ON users(league_group_id);
            CREATE INDEX IF NOT EXISTS idx_web_users_group ON web_users(league_group_id);
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

# Лига деңгейлері (3 деңгей, мини-топтармен)
LEAGUES = ["bronze", "silver", "gold"]
LEAGUE_NAMES = {
    "bronze": "🥉 Қола",
    "silver": "🥈 Күміс", 
    "gold": "🥇 Алтын"
}

# Лигаға көтерілу/түсу үшін қажетті орын
PROMOTION_THRESHOLD = 7  # Топ 7 көтеріледі (Duolingo: 7-10)
DEMOTION_THRESHOLD = 5   # Соңғы 5 түседі (Duolingo: 5-10)


def get_league_index(league: str) -> int:
    """Лига индексін алу"""
    try:
        return LEAGUES.index(league.lower())
    except ValueError:
        return 0  # bronze по умолчанию


def get_current_week_start() -> str:
    """Ағымдағы аптаның басталу күнін алу (дүйсенбі)"""
    import datetime
    today = datetime.date.today()
    # 0 = Monday, 6 = Sunday
    days_since_monday = today.weekday()
    monday = today - datetime.timedelta(days=days_since_monday)
    return monday.isoformat()


async def get_or_create_league_group(league: str, user_source: str = 'telegram') -> int:
    """Пайдаланушы үшін лига тобын алу немесе жасау (Duolingo стилінде)
    
    Әр аптада жаңа топтар жасалады. Қолданушы алғаш рет апта ішінде 
    ұпай жинағанда, оны бос топқа қосады немесе жаңа топ жасайды.
    """
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        week_start = get_current_week_start()
        
        # Ағымдағы аптадағы бос топты табу (GROUP_MAX_SIZE-тан кем қолданушылары бар)
        async with conn.execute("""
            SELECT lg.id, COUNT(CASE WHEN u.user_id IS NOT NULL THEN 1 END) + 
                   COUNT(CASE WHEN wu.email IS NOT NULL THEN 1 END) as user_count
            FROM league_groups lg
            LEFT JOIN users u ON u.league_group_id = lg.id
            LEFT JOIN web_users wu ON wu.league_group_id = lg.id
            WHERE lg.league = ? AND lg.week_start = ?
            GROUP BY lg.id
            HAVING user_count < ?
            ORDER BY lg.id ASC
            LIMIT 1
        """, (league, week_start, GROUP_MAX_SIZE)) as cur:
            row = await cur.fetchone()
            if row:
                return row['id']
        
        # Бос топ жоқ - жаңа топ жасау
        cursor = await conn.execute(
            "INSERT INTO league_groups (league, week_start) VALUES (?, ?)",
            (league, week_start)
        )
        await conn.commit()
        return cursor.lastrowid


async def assign_user_to_group(user_id: int = None, email: str = None) -> None:
    """Қолданушыны топқа тағайындау (алғаш ұпай алғанда)"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        
        if user_id:
            # Telegram қолданушы
            async with conn.execute(
                "SELECT league, league_group_id, weekly_points FROM users WHERE user_id = ?",
                (user_id,)
            ) as cur:
                user = await cur.fetchone()
                if not user:
                    return
                
                # Егер бұл аптада топ тағайындалмаған болса және ұпай алса
                week_start = get_current_week_start()
                if user['league_group_id']:
                    # Тексеру: топ ағымдағы апта үшін ме?
                    async with conn.execute(
                        "SELECT week_start FROM league_groups WHERE id = ?",
                        (user['league_group_id'],)
                    ) as cur2:
                        group = await cur2.fetchone()
                        if group and group['week_start'] == week_start:
                            return  # Қолданушы қазірдің өзінде дұрыс топта
                
                # Жаңа топқа қосу
                group_id = await get_or_create_league_group(user['league'], 'telegram')
                await conn.execute(
                    "UPDATE users SET league_group_id = ? WHERE user_id = ?",
                    (group_id, user_id)
                )
        
        elif email:
            # Веб қолданушы
            async with conn.execute(
                "SELECT league, league_group_id, weekly_points FROM web_users WHERE email = ?",
                (email,)
            ) as cur:
                user = await cur.fetchone()
                if not user:
                    return
                
                week_start = get_current_week_start()
                if user['league_group_id']:
                    async with conn.execute(
                        "SELECT week_start FROM league_groups WHERE id = ?",
                        (user['league_group_id'],)
                    ) as cur2:
                        group = await cur2.fetchone()
                        if group and group['week_start'] == week_start:
                            return
                
                group_id = await get_or_create_league_group(user['league'], 'web')
                await conn.execute(
                    "UPDATE web_users SET league_group_id = ? WHERE email = ?",
                    (group_id, email)
                )
        
        await conn.commit()


async def mark_solved_and_add_point(user_id: int, task_id: int) -> None:
    """Telegram қолданушы есепті шешіп ұпай алады (жалпы және апта)"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        await conn.execute(
            "INSERT OR REPLACE INTO user_solutions (user_id, task_id, is_correct) VALUES (?, ?, 1)",
            (user_id, task_id)
        )
        
        # Алдымен weekly_points-ты тексеру
        async with conn.execute(
            "SELECT weekly_points FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            was_zero = row and row[0] == 0
        
        await conn.execute(
            "UPDATE users SET points = points + 1, solved_count = solved_count + 1, weekly_points = weekly_points + 1 WHERE user_id = ?",
            (user_id,)
        )
        await conn.commit()
        
        # Егер бұл аптадағы алғаш ұпай болса, топқа қосу
        if was_zero:
            await assign_user_to_group(user_id=user_id)


async def mark_web_solved_and_add_point(email: str, task_id: int) -> None:
    """Веб қолданушы есепті дұрыс шешкен кезде (жалпы және апта)"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        await conn.execute(
            "INSERT OR REPLACE INTO web_user_solutions (email, task_id, is_correct) VALUES (?, ?, 1)",
            (email, task_id)
        )
        
        # Алдымен weekly_points-ты тексеру
        async with conn.execute(
            "SELECT weekly_points FROM web_users WHERE email = ?", (email,)
        ) as cur:
            row = await cur.fetchone()
            was_zero = row and row[0] == 0
        
        await conn.execute(
            "UPDATE web_users SET points = points + 1, solved_count = solved_count + 1, weekly_points = weekly_points + 1 WHERE email = ?",
            (email,)
        )
        await conn.commit()
        
        # Егер бұл аптадағы алғаш ұпай болса, топқа қосу
        if was_zero:
            await assign_user_to_group(email=email)


async def get_league_leaderboard(league: str, limit: int = 30, group_id: int = None) -> List[Dict[str, Any]]:
    """Белгілі бір лиганың рейтингін алу (апталық ұпай бойынша)
    
    Егер group_id көрсетілсе, тек сол топтағы қолданушылар көрсетіледі.
    Егер group_id = None болса, барлық топтар біріктіріледі (ескі мінез-құлық).
    """
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        
        if group_id is not None:
            # Белгілі топтағы қолданушылар
            async with conn.execute(
                """
                SELECT user_id, username, full_name, NULL as email, NULL as name, NULL as nickname,
                       points, solved_count, weekly_points, league, league_group_id, 'telegram' as source
                FROM users
                WHERE league = ? AND league_group_id = ?
                UNION ALL
                SELECT NULL as user_id, NULL as username, NULL as full_name, 
                       email, name, nickname, points, solved_count, weekly_points, league, league_group_id, 'web' as source
                FROM web_users
                WHERE league = ? AND league_group_id = ? AND nickname IS NOT NULL AND nickname != ''
                ORDER BY weekly_points DESC, points DESC
                LIMIT ?
                """, (league, group_id, league, group_id, limit)
            ) as cur:
                return [dict(row) for row in await cur.fetchall()]
        else:
            # Барлық топтар (ескі API үйлесімділігі үшін)
            async with conn.execute(
                """
                SELECT user_id, username, full_name, NULL as email, NULL as name, NULL as nickname,
                       points, solved_count, weekly_points, league, league_group_id, 'telegram' as source
                FROM users
                WHERE league = ?
                UNION ALL
                SELECT NULL as user_id, NULL as username, NULL as full_name, 
                       email, name, nickname, points, solved_count, weekly_points, league, league_group_id, 'web' as source
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
            "SELECT league, weekly_points, points, league_group_id FROM users WHERE user_id = ?", 
            (user_id,)
        ) as cur:
            row = await cur.fetchone()
            if not row:
                return None
            
            result = dict(row)
            
            # Лигадағы орынды табу (тек өз тобында)
            if result.get('league_group_id'):
                leaderboard = await get_league_leaderboard(
                    result['league'], 
                    limit=100, 
                    group_id=result['league_group_id']
                )
            else:
                # Топ жоқ болса, барлық лига (ескі мінез-құлық)
                leaderboard = await get_league_leaderboard(result['league'], limit=100)
            
            for i, user in enumerate(leaderboard):
                if user.get('user_id') == user_id:
                    result['rank'] = i + 1
                    break
            
            return result


async def get_web_user_league_info(email: str) -> Optional[Dict[str, Any]]:
    """Веб қолданушының лига ақпаратын алу"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            "SELECT league, weekly_points, points, league_group_id FROM web_users WHERE email = ?", 
            (email,)
        ) as cur:
            row = await cur.fetchone()
            if not row:
                return None
            
            result = dict(row)
            
            # Лигадағы орынды табу (тек өз тобында)
            if result.get('league_group_id'):
                leaderboard = await get_league_leaderboard(
                    result['league'], 
                    limit=100, 
                    group_id=result['league_group_id']
                )
            else:
                # Топ жоқ болса, барлық лига
                leaderboard = await get_league_leaderboard(result['league'], limit=100)
            
            for i, user in enumerate(leaderboard):
                if user.get('email') == email:
                    result['rank'] = i + 1
                    break
            
            return result


async def reset_weekly_points() -> None:
    """Апталық ұпайларды нөлге тастау және лигаларды жаңарту (топ бойынша)"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        
        # Әр лига үшін топ бойынша көтерілу/түсу
        for i, league in enumerate(LEAGUES):
            # Ағымдағы аптадағы барлық топтарды алу
            week_start = get_current_week_start()
            async with conn.execute(
                "SELECT id FROM league_groups WHERE league = ? AND week_start = ?",
                (league, week_start)
            ) as cur:
                groups = await cur.fetchall()
            
            # Әр топ үшін жеке көтерілу/түсу
            for group in groups:
                group_id = group['id']
                leaderboard = await get_league_leaderboard(league, limit=100, group_id=group_id)
                
                # Топ 7 - көтеріледі (соңғы лигадан басқа)
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
                
                # Соңғы 5 - түседі (бірінші лигадан басқа)
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
        
        # Барлық апталық ұпайларды нөлге тастау және топтарды тазалау
        await conn.execute("UPDATE users SET weekly_points = 0, league_group_id = NULL")
        await conn.execute("UPDATE web_users SET weekly_points = 0, league_group_id = NULL")
        await conn.commit()


# ==================== ЖЕТІСТІКТЕР (ACHIEVEMENTS) ====================

# Жетістіктер анықтамасы
ACHIEVEMENTS = {
    # Есеп шешу жетістіктері
    "first_solve": {
        "id": "first_solve",
        "name": "🌟 Бірінші қадам",
        "description": "Алғашқы есепті шеш",
        "icon": "🌟",
        "requirement": {"type": "solved_count", "value": 1}
    },
    "solver_10": {
        "id": "solver_10",
        "name": "🔢 Математик",
        "description": "10 есеп шеш",
        "icon": "🔢",
        "requirement": {"type": "solved_count", "value": 10}
    },
    "solver_50": {
        "id": "solver_50",
        "name": "📚 Білгір",
        "description": "50 есеп шеш",
        "icon": "📚",
        "requirement": {"type": "solved_count", "value": 50}
    },
    "solver_100": {
        "id": "solver_100",
        "name": "🎓 Ұстаз",
        "description": "100 есеп шеш",
        "icon": "🎓",
        "requirement": {"type": "solved_count", "value": 100}
    },
    "solver_500": {
        "id": "solver_500",
        "name": "🏆 Чемпион",
        "description": "500 есеп шеш",
        "icon": "🏆",
        "requirement": {"type": "solved_count", "value": 500}
    },
    
    # Ұпай жетістіктері
    "points_25": {
        "id": "points_25",
        "name": "⚡ Жылдам бастама",
        "description": "25 ұпай жина",
        "icon": "⚡",
        "requirement": {"type": "points", "value": 25}
    },
    "points_100": {
        "id": "points_100",
        "name": "💎 Жүз ұпай",
        "description": "100 ұпай жина",
        "icon": "💎",
        "requirement": {"type": "points", "value": 100}
    },
    "points_500": {
        "id": "points_500",
        "name": "👑 Патша",
        "description": "500 ұпай жина",
        "icon": "👑",
        "requirement": {"type": "points", "value": 500}
    },
    
    # Лига жетістіктері
    "league_silver": {
        "id": "league_silver",
        "name": "🥈 Күміс лига",
        "description": "Күміс лигаға көтеріл",
        "icon": "🥈",
        "requirement": {"type": "league", "value": "silver"}
    },
    "league_gold": {
        "id": "league_gold",
        "name": "🥇 Алтын лига",
        "description": "Алтын лигаға көтеріл",
        "icon": "🥇",
        "requirement": {"type": "league", "value": "gold"}
    },
}


async def get_user_achievements(email: str) -> List[Dict[str, Any]]:
    """Қолданушының барлық жетістіктерін алу"""
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            "SELECT achievement_id, unlocked_at FROM web_user_achievements WHERE email = ?",
            (email,)
        ) as cur:
            unlocked = {row['achievement_id']: row['unlocked_at'] for row in await cur.fetchall()}
    
    # Барлық жетістіктерді қайтару (ашылғандар мен ашылмағандар)
    result = []
    for ach_id, ach in ACHIEVEMENTS.items():
        result.append({
            **ach,
            "unlocked": ach_id in unlocked,
            "unlocked_at": unlocked.get(ach_id)
        })
    return result


async def unlock_achievement(email: str, achievement_id: str) -> bool:
    """Жетістікті ашу (егер бұрын ашылмаған болса)"""
    if achievement_id not in ACHIEVEMENTS:
        return False
    
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        try:
            await conn.execute(
                "INSERT OR IGNORE INTO web_user_achievements (email, achievement_id) VALUES (?, ?)",
                (email, achievement_id)
            )
            await conn.commit()
            return True
        except Exception:
            return False


async def check_and_unlock_achievements(email: str) -> List[str]:
    """Қолданушының статистикасына сәйкес жетістіктерді тексеру және ашу"""
    # Қолданушы статистикасын алу
    stats = await get_web_user_stats(email)
    if not stats:
        return []
    
    # Ашылған жетістіктерді алу
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            "SELECT achievement_id FROM web_user_achievements WHERE email = ?",
            (email,)
        ) as cur:
            already_unlocked = {row['achievement_id'] for row in await cur.fetchall()}
    
    newly_unlocked = []
    
    for ach_id, ach in ACHIEVEMENTS.items():
        if ach_id in already_unlocked:
            continue
        
        req = ach["requirement"]
        should_unlock = False
        
        if req["type"] == "solved_count":
            should_unlock = stats.get("solved_count", 0) >= req["value"]
        elif req["type"] == "points":
            should_unlock = stats.get("points", 0) >= req["value"]
        elif req["type"] == "league":
            should_unlock = stats.get("league") == req["value"]
        
        if should_unlock:
            if await unlock_achievement(email, ach_id):
                newly_unlocked.append(ach_id)
    
    return newly_unlocked