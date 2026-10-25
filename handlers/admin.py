from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.repositories import scope_for, set_entry_status, get_pending

router = Router()


async def is_group_admin(message: Message) -> bool:
    if message.chat.type == "private":
        return False
    try:
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in {"administrator", "creator"}
    except Exception:
        return False


@router.message(Command("approve"))
async def approve_command(message: Message):
    if not await is_group_admin(message):
        await message.answer("Only group admins can approve entries.")
        return
    try:
        entry_id = int((message.text or "").split(maxsplit=1)[1])
    except (IndexError, ValueError):
        await message.answer("Usage: /approve ENTRY_ID")
        return
    scope_id, _ = scope_for(message)
    entry = await get_pending(scope_id, entry_id)
    if not entry:
        await message.answer("Pending entry not found.")
        return
    await set_entry_status(scope_id, entry_id, "approved")
    await message.answer(f"✅ Entry #{entry_id} approved and now searchable.")


@router.message(Command("reject"))
async def reject_command(message: Message):
    if not await is_group_admin(message):
        await message.answer("Only group admins can reject entries.")
        return
    try:
        entry_id = int((message.text or "").split(maxsplit=1)[1])
    except (IndexError, ValueError):
        await message.answer("Usage: /reject ENTRY_ID")
        return
    scope_id, _ = scope_for(message)
    entry = await get_pending(scope_id, entry_id)
    if not entry:
        await message.answer("Pending entry not found.")
        return
    await set_entry_status(scope_id, entry_id, "rejected")
    await message.answer(f"Entry #{entry_id} rejected.")
