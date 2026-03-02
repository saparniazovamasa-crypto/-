from bot import bot
import aiosqlite
from time import time
from aiogram.filters import BaseFilter
from aiogram.types import (
    Message,
    ChatMemberAdministrator,
    ChatMemberOwner,
    CallbackQuery,
)

_flood_tracker: dict[int, list[float]] = {}
_blocked_until: dict[int, float] = {}


class IsBanBot(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = (
            event.from_user.id if isinstance(event, Message) else event.from_user.id
        )
        now = time()
        if user_id in _blocked_until and _blocked_until[user_id] > now:
            return False
        if user_id not in _flood_tracker:
            _flood_tracker[user_id] = []
        _flood_tracker[user_id] = [t for t in _flood_tracker[user_id] if now - t < 180]
        _flood_tracker[user_id].append(now)

        if len(_flood_tracker[user_id]) > 10:
            _blocked_until[user_id] = now + 300
            return False
        async with aiosqlite.connect("bot.db") as db:
            cur = await db.execute(
                "SELECT is_banned FROM bans WHERE user_id=?", (user_id,)
            )
            row = await cur.fetchone()

        if row is not None and row[0] == 1:
            return False

        return True


class IsBan(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        member = await message.chat.get_member(message.from_user.id)

        if member.status == "creator":
            return True

        if member.status == "administrator" and getattr(
            member, "can_restrict_members", False
        ):
            return True

        await message.answer(
            "ты либо не админ, либо ты ебучая феминистка без права бана"
        )
        return False


class IsBanQuery(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        member = await callback.message.chat.get_member(callback.from_user.id)

        if member.status == "creator":
            return True

        if member.status == "administrator" and getattr(
            member, "can_restrict_members", False
        ):
            return True

        await callback.answer(
            "ты либо не админ, либо ты ебучая феминистка без права бана",
            show_alert=True,
        )
        return False


class IsMute(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        member = await message.chat.get_member(message.from_user.id)

        if member.status == "creator":
            return True

        if member.status == "administrator" and getattr(
            member, "can_delete_messages", False
        ):
            return True

        await message.answer(
            "ты либо не админ, либо ты феминистка без права на удаление сообщений"
        )
        return False


class IsMuteQuery(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        member = await callback.message.chat.get_member(callback.from_user.id)

        if member.status == "creator":
            return True

        if member.status == "administrator" and getattr(
            member, "can_delete_messages", False
        ):
            return True

        await callback.answer(
            "ты либо не админ, либо ты феминистка без права на удаление сообщений",
            show_alert=True,
        )
        return False


async def is_admin(chat_id: int, user_id: int) -> bool:
    member = await bot.get_chat_member(chat_id, user_id)
    return isinstance(member, (ChatMemberAdministrator, ChatMemberOwner))


async def resolve_user_id(chat_id: int, username: str) -> int | None:
    try:
        if not username.startswith("@"):
            username = "@" + username

        member = await bot.get_chat_member(chat_id, username)
        return member.user.id
    except Exception:
        try:
            user = await bot.get_chat(username)
            return user.id
        except Exception:
            return None
