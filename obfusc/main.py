import asyncio
from moderation import (
    banbot_command,
    unbanbot_command,
    ban_command,
    unban_command,
    mute_command,
    unmute_command,
    kick_command,
    warn_command,
    warns_command,
    unwarn_command,
)
from bot import lchat_id
from utils import IsBanBot, IsBan, IsMute, IsBanQuery, IsMuteQuery
from callback_query import unban_callback, unmute_callback, invite_link_callback
from db import init_db
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    Message,
    ChatInviteLink,
    InlineKeyboardButton,
    ChatMemberUpdated,
)

bot = Bot(
    "8530530096:AAHwKe0zk11T99DrLCB-oz01wTzwjBu_MyY",
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()

dp.message.register(ban_command, Command("ban"), IsBanBot(), IsBan())
dp.message.register(unban_command, Command("unban"), IsBanBot(), IsBan())
dp.message.register(mute_command, Command("mute"), IsBanBot(), IsMute())
dp.message.register(unmute_command, Command("unmute"), IsBanBot(), IsMute())
dp.message.register(kick_command, Command("kick"), IsBanBot(), IsBan())
dp.message.register(warn_command, Command("warn"), IsBanBot(), IsBan())
dp.message.register(warns_command, Command("warns"), IsBanBot(), IsBan())
dp.message.register(unwarn_command, Command("unwarn"), IsBanBot(), IsBan())
dp.message.register(banbot_command, Command("banbot"), IsBanBot())
dp.message.register(unbanbot_command, Command("unbanbot"), IsBanBot())
dp.callback_query.register(
    unban_callback, lambda cb: cb.data.startswith("unban:"), IsBanBot(), IsBanQuery()
)
dp.callback_query.register(
    unmute_callback, lambda cb: cb.data.startswith("unmute:"), IsBanBot(), IsMuteQuery()
)
dp.callback_query.register(
    invite_link_callback, lambda cb: cb.data == "invite_link", IsBanBot()
)


@dp.my_chat_member()
async def on_bot_added_or_removed(event: ChatMemberUpdated):
    chat = event.chat

    if chat.type not in ["group", "supergroup"]:
        return

    if event.old_chat_member.status in [
        "left",
        "kicked",
    ] and event.new_chat_member.status in ["member", "administrator"]:
        if chat.id != lchat_id:
            try:
                await bot.send_message(chat.id, "пососи хуй")
                await bot.leave_chat(chat.id)
            except Exception as e:
                print(f"Error: {e}")


@dp.message(Command("start"), IsBanBot())
async def start_handler(message: Message, command: Command):
    keyboard = InlineKeyboardBuilder(
        [
            [
                InlineKeyboardButton(text="ссылка", callback_data="invite_link"),
                InlineKeyboardButton(text="переходник", url="https://t.me/+ygvtMXLwrepmYjRi"),
            ],
        ],
    )
    if command.args:
        return
    if message.from_user.id == 7607280952:
        await message.answer("🪙")
        await message.answer(
            "Пр-рррветик мой любимый парсер-р~\nдобавь меня в чатик и я буду банить нахуй всех неугодных\nполучить ссылочку на вход /invite"
        )
    else:
        await message.answer("🪙")
        await message.answer(
            "привет, это бот для создания ссылок для входа в чат\n"
            "для создания ссылки используй кнопку ниже",
            reply_markup=keyboard.as_markup(),
        )


@dp.message(Command("invite"), IsBanBot())
async def invite_link(message: Message):
    try:
        expire_date = datetime.now(ZoneInfo("Europe/Moscow")) + timedelta(minutes=1)
        invite_link: ChatInviteLink = await bot.create_chat_invite_link(
            chat_id=lchat_id,
            expire_date=expire_date,
            creates_join_request=True,
            name=f"для {message.from_user.full_name}",
        )

        await message.answer(
            f"🔗 Ссылка по заявке (на 1 минуту):\n{invite_link.invite_link}",
            disable_web_page_preview=True,
        )

        await asyncio.sleep(60)
        await bot.revoke_chat_invite_link(
            chat_id=lchat_id, invite_link=invite_link.invite_link
        )

    except Exception as e:
        await message.answer(f"error: {e}")


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
