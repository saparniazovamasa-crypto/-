import asyncio
from bot import bot, lchat_id
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from aiogram.types import (
    ChatInviteLink,
    CallbackQuery,
    ChatPermissions,
)


async def unmute_callback(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    chat_id = callback.message.chat.id

    try:
        await bot.restrict_chat_member(
            chat_id,
            user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_invite_users=False,
                can_change_info=False,
                can_pin_messages=False,
            ),
        )
        await callback.message.edit_text("пидор размучен")
    except Exception as e:
        await callback.message.answer(f"errar syka\n<code>{e}</code>")


async def unban_callback(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    chat_id = callback.message.chat.id

    try:
        await bot.unban_chat_member(chat_id, user_id)
        await callback.message.edit_text(f"пидор разбанен")
    except Exception as e:
        await callback.answer(f"errar syka: {e}")


async def invite_link_callback(callback: CallbackQuery):
    try:
        expire_date = datetime.now(ZoneInfo("Europe/Moscow")) + timedelta(minutes=1)
        invite_link: ChatInviteLink = await bot.create_chat_invite_link(
            chat_id=lchat_id,
            expire_date=expire_date,
            creates_join_request=True,
            name=f"для {callback.from_user.full_name}",
        )

        msg = await callback.message.answer(
            f"🔗 Ссылка по заявке (на 1 минуту):\n{invite_link.invite_link}",
            disable_web_page_preview=True,
        )

        await asyncio.sleep(60)
        await msg.delete()
        await bot.revoke_chat_invite_link(
            chat_id=lchat_id, invite_link=invite_link.invite_link
        )
    except Exception as e:
        await callback.message.answer(f"errar syka: {e}")
