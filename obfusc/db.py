from datetime import datetime
from zoneinfo import ZoneInfo
import aiosqlite


async def init_db():
    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS warns (
                chat_id INTEGER,
                user_id INTEGER,
                reason TEXT,
                time TEXT
            )
        """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS bans (
                user_id INTEGER PRIMARY KEY,
                is_banned BOOLEAN
            )
        """
        )
        await db.commit()


async def is_banned(user_id: int) -> bool:
    async with aiosqlite.connect("bot.db") as db:
        cur = await db.execute("SELECT is_banned FROM bans WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return row is not None and row[0] == 1


async def ban_user(user_id: int):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            "INSERT INTO bans (user_id, is_banned) VALUES (?, 1) "
            "ON CONFLICT(user_id) DO UPDATE SET is_banned=1",
            (user_id,),
        )
        await db.commit()


async def unban_user(user_id: int):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            "INSERT INTO bans (user_id, is_banned) VALUES (?, 0) "
            "ON CONFLICT(user_id) DO UPDATE SET is_banned=0",
            (user_id,),
        )
        await db.commit()


async def add_warn(chat_id: int, user_id: int, reason: str):
    time_now = datetime.now(ZoneInfo("Europe/Moscow")).strftime("%d.%m")

    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            "INSERT INTO warns (chat_id, user_id, reason, time) VALUES (?, ?, ?, ?)",
            (chat_id, user_id, reason, time_now),
        )
        await db.commit()

        cur = await db.execute(
            "SELECT COUNT(*) FROM warns WHERE chat_id=? AND user_id=?",
            (chat_id, user_id),
        )
        row = await cur.fetchone()
        return row[0]


async def remove_warns(chat_id: int, user_id: int):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            "DELETE FROM warns WHERE chat_id=? AND user_id=?", (chat_id, user_id)
        )
        await db.commit()


async def get_warns(chat_id: int, user_id: int) -> int:
    async with aiosqlite.connect("bot.db") as db:
        cur = await db.execute(
            "SELECT COUNT(*) FROM warns WHERE chat_id=? AND user_id=?",
            (chat_id, user_id),
        )
        row = await cur.fetchone()
        return row[0] if row else 0
