from bot import bot, admins
from db import add_warn, remove_warns, get_warns
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import aiosqlite
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPermissions,
)
from utils import is_admin, resolve_user_id


async def banbot_command(message: Message):
    if message.from_user.id not in admins:
        await message.answer("ты не парсер, пидор")
        return

    user_id = None

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id

    elif message.text.split(maxsplit=1)[1:]:
        arg = message.text.split(maxsplit=1)[1]

        if arg.startswith("@"):
            user_id = await resolve_user_id(message.chat.id, arg)
            if user_id is None:
                await message.answer(
                    "не нашел пидора мне кажется ты хочешь меня наебать"
                )
                return
        elif arg.isdigit():
            user_id = int(arg)

    if not user_id:
        await message.answer("юзай айди или реплай, пидор")
        return

    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            "INSERT OR REPLACE INTO bans (user_id, is_banned) VALUES (?, ?)",
            (user_id, 1),
        )
        await db.commit()

    await message.answer(
        f"🚫 сын шлюхи пидорской <code>{user_id}</code> забанен в боте"
    )


async def unbanbot_command(message: Message):
    if message.from_user.id not in admins:
        return await message.answer("ты не парсер, пидор")
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif message.text.split(maxsplit=1)[1:]:
        arg = message.text.split(maxsplit=1)[1]
        if arg.isdigit():
            user_id = int(arg)

    if not user_id:
        await message.answer("юзай айди или реплай, пидор")
        return

    async with aiosqlite.connect("bot.db") as db:
        await db.execute("DELETE FROM bans WHERE user_id = ?", (user_id,))
        await db.commit()

    await message.answer(f"пидор <code>{user_id}</code> разбанен в боте")


async def ban_command(message: Message):

    args = message.text.strip().split(maxsplit=3)

    user_id = None
    duration = None
    reason = "нету"
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id

        if len(args) >= 2:
            try:
                duration = int(args[1])
            except ValueError:
                reason = args[1]
            if len(args) >= 3:
                reason = args[2]

    elif len(args) >= 2:
        try:
            user_id = int(args[1])
        except ValueError:
            return await message.answer("айди укажи числом, пидор")

        if len(args) >= 3:
            try:
                duration = int(args[2])
            except ValueError:
                reason = args[2]
            if len(args) == 4:
                reason = args[3]

    else:
        return await message.answer("используй /ban юзер_ид/реплай время причина")

    if not user_id:
        return await message.answer("нормально укажи пидор")

    if await is_admin(message.chat.id, user_id):
        return await message.answer("нах ты админа банить собрался, пидор")

    if duration:
        until = datetime.now(ZoneInfo("Europe/Moscow")) + timedelta(minutes=duration)
    else:
        until = None

    try:
        await bot.ban_chat_member(message.chat.id, user_id, until_date=until)

        dur_text = f"{duration} мин." if duration else "навсегда"
        keyboard = InlineKeyboardBuilder(
            [
                [
                    InlineKeyboardButton(
                        text="разбанить", callback_data=f"unban:{user_id}"
                    ),
                ],
            ],
        )
        await message.answer(
            f"пидор забанен на {dur_text}\nпричина: {reason}",
            reply_markup=keyboard.as_markup(),
        )
    except Exception as e:
        await message.answer(f"errar syka:\n<code>{e}</code>")


async def unban_command(message: Message):
    args = message.text.strip().split()
    user_id = None

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(args) >= 2:
        try:
            user_id = int(args[1])
        except ValueError:
            return await message.answer("айди должен быть числом, пидор")
    else:
        return await message.answer("укажи айди или сделай реплай, пидор")

    try:
        await bot.unban_chat_member(message.chat.id, user_id)
        await message.answer(f"пидор {user_id} разбанен")
    except Exception as e:
        await message.answer(f"не получилось разбанить: {e}")


async def mute_command(message: Message):

    args = message.text.strip().split(maxsplit=3)

    user_id = None
    duration = None
    reason = "нету"
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id

        if len(args) >= 2:
            try:
                duration = int(args[1])
            except ValueError:
                reason = args[1]
            if len(args) >= 3:
                reason = args[2]

    elif len(args) >= 2:
        try:
            user_id = int(args[1])
        except ValueError:
            return await message.answer("айди укажи числом, пидор")

        if len(args) >= 3:
            try:
                duration = int(args[2])
            except ValueError:
                reason = args[2]
            if len(args) == 4:
                reason = args[3]

    else:
        return await message.answer("используй /mute юзер_ид/реплай [время] [причина]")

    if not user_id:
        return await message.answer("нормально укажи пидор")

    if await is_admin(message.chat.id, user_id):
        return await message.answer("нах ты админа мутить собрался, пидор")

    if duration:
        until = datetime.now(ZoneInfo("Europe/Moscow")) + timedelta(minutes=duration)
    else:
        until = None

    permissions = ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_change_info=False,
        can_invite_users=False,
        can_pin_messages=False,
    )

    try:
        await bot.restrict_chat_member(
            message.chat.id, user_id, permissions=permissions, until_date=until
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="размутить", callback_data=f"unmute:{user_id}"
                    )
                ]
            ]
        )

        dur_text = f"{duration} мин." if duration else "навсегда"
        await message.answer(
            f"пидор замучен на {dur_text}\nпричина: {reason}", reply_markup=keyboard
        )
    except Exception as e:
        await message.answer(f"ошибка при муте:\n<code>{e}</code>")


async def unmute_command(message: Message):
    args = message.text.strip().split()
    user_id = None

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(args) >= 2:
        try:
            user_id = int(args[1])
        except ValueError:
            return await message.answer("айди должен быть числом, пидор")
    else:
        return await message.answer("укажи айди или сделай реплай, пидор")

    try:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
            ),
        )
        await message.answer(f"пидор {user_id} размучен")
    except Exception as e:
        await message.answer(f"errar syka: {e}")


async def kick_command(message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        await message.answer("ты не админ, сьебись отсюда")
        return

    args = message.text.split()
    user_id = None
    reason = "нету"

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        if len(args) >= 2:
            reason = " ".join(args[1:])
    elif len(args) >= 2:
        username_or_id = args[1]

        try:
            user_id = int(username_or_id)
        except ValueError:
            return await message.answer("айди должен быть числом, пидор")

        if len(args) > 2:
            reason = " ".join(args[2:])
    else:
        await message.answer("юзай /kick реплай причина")
        return

    try:
        if await is_admin(message.chat.id, user_id):
            await message.answer("нах ты админов кикать собрался? иди нахуй")
            return
        await bot.ban_chat_member(message.chat.id, user_id)
        await bot.unban_chat_member(message.chat.id, user_id)
    except Exception as e:
        await message.answer(f"errar syka: {e}")
        return

    await message.answer(f"пидор был кикнут\nпричина: {reason}")


async def warn_command(message: Message):
    args = message.text.strip().split(maxsplit=2)

    if not message.reply_to_message and len(args) < 2:
        return await message.answer("укажи пидора через реплай или айди")

    user_id = None
    reason = "нету"

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        if len(args) >= 2:
            reason = args[1] if len(args) == 2 else args[2]
    else:
        try:
            user_id = int(args[1])
        except ValueError:
            return await message.answer(
                "не смог найти юзера, мне кажется ты хочешь меня наебать"
            )

        if len(args) == 3:
            reason = args[2]

    if await is_admin(message.chat.id, user_id):
        return await message.answer("нах ты админов варнить собрался? иди нахуй")

    WARN_LIMIT = 3
    chat_id = message.chat.id
    count = await add_warn(chat_id, user_id, reason)

    if count >= WARN_LIMIT:
        await bot.ban_chat_member(chat_id, user_id)
        await message.answer(
            f"пидор получил {count} варна и был забанен\nпоследняя причина: {reason}"
        )
        await remove_warns(chat_id, user_id)
    else:
        await message.answer(f"выдал варн ({count}/{WARN_LIMIT})\nпричина: {reason}")


async def unwarn_command(message: Message):
    args = message.text.strip().split()
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(args) >= 2:
        try:
            user_id = int(args[1])
        except ValueError:
            return await message.answer("айди должен быть числом, пидор")
    else:
        return await message.answer("укажи айди или сделай реплай, пидор")

    await remove_warns(message.chat.id, user_id)
    await message.answer("варны пидора удалены")


async def warns_command(message: Message):
    args = message.text.strip().split()
    user_id = None
    chat_id = message.chat.id

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(args) >= 2:
        try:
            user_id = int(args[1])
        except ValueError:
            return await message.answer("айди должен быть числом, пидор")
    else:
        return await message.answer("укажи айди или сделай реплай, пидор")
    async with aiosqlite.connect("warns.db") as db:
        cur = await db.execute(
            "SELECT reason, time FROM warns WHERE chat_id=? AND user_id=?",
            (chat_id, user_id),
        )
        rows = await cur.fetchall()

    if not rows:
        await message.answer("у пидора нет варнов")
        return

    text = f"варны пидора ({len(rows)}):\n"
    for i, (reason, time) in enumerate(rows, start=1):
        text += f"{i}. {reason} — {time}\n"

    await message.answer(text)
