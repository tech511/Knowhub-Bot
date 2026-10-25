from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest
from config import MAX_TITLE_LENGTH, MAX_CONTENT_LENGTH, PAGE_SIZE
from database.repositories import scope_for, create_entry, search_entries, update_entry, delete_entry
from keyboards.main_menu import page_keyboard

router = Router()


class SaveFlow(StatesGroup):
    title = State()
    content = State()
    category = State()
    tags = State()


class EditFlow(StatesGroup):
    payload = State()


def parse_id(text):
    try:
        return int(text.split(maxsplit=1)[1])
    except (IndexError, ValueError):
        return None


@router.message(Command("save"))
async def save_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(SaveFlow.title)
    await message.answer("Send a short title for this entry (max 120 characters).")


@router.message(SaveFlow.title)
async def save_title(message: Message, state: FSMContext):
    title = (message.text or "").strip()
    if not title or len(title) > MAX_TITLE_LENGTH:
        await message.answer(f"Title must be 1–{MAX_TITLE_LENGTH} characters. Try again.")
        return
    await state.update_data(title=title)
    await state.set_state(SaveFlow.content)
    await message.answer("Now send the text or useful URL to save (max 3500 characters).")


@router.message(SaveFlow.content)
async def save_content(message: Message, state: FSMContext):
    content = (message.text or "").strip()
    if not content or len(content) > MAX_CONTENT_LENGTH:
        await message.answer(f"Content must be 1–{MAX_CONTENT_LENGTH} characters. Try again.")
        return
    await state.update_data(content=content)
    await state.set_state(SaveFlow.category)
    await message.answer("Enter a category (e.g. guides, FAQs, rules, tutorials, resources).")


@router.message(SaveFlow.category)
async def save_category(message: Message, state: FSMContext):
    category = (message.text or "general").strip()[:40].lower()
    await state.update_data(category=category or "general")
    await state.set_state(SaveFlow.tags)
    await message.answer("Enter comma-separated tags, or send - to skip.")


@router.message(SaveFlow.tags)
async def save_tags(message: Message, state: FSMContext):
    tags_text = (message.text or "-").strip()
    data = await state.get_data()
    tags = [] if tags_text == "-" else [x.strip() for x in tags_text.split(",") if x.strip()][:10]
    scope_id, scope_type = scope_for(message)
    status = "pending" if scope_type == "group" else "approved"
    entry = await create_entry(
        scope_id=scope_id, scope_type=scope_type, owner_id=message.from_user.id,
        title=data["title"], content=data["content"], category=data["category"],
        tags=tags, status=status,
    )
    await state.clear()
    if status == "pending":
        await message.answer(
            f"✅ Submitted as entry <b>#{entry['entry_id']}</b> for admin approval.\n"
            "A group admin can approve it with /approve " + str(entry["entry_id"])
        )
    else:
        await message.answer(f"✅ Saved as entry <b>#{entry['entry_id']}</b>.")


@router.message(Command("myentries"))
async def my_entries(message: Message):
    scope_id, _ = scope_for(message)
    entries, total = await search_entries(scope_id, "", page=0, page_size=PAGE_SIZE, owner_id=message.from_user.id)
    if not entries:
        await message.answer("You don't have any approved entries here yet. Use /save to add one.")
        return
    await message.answer(f"Your entries ({total}):", reply_markup=page_keyboard(entries, 0, total, PAGE_SIZE))


@router.message(Command("edit"))
async def edit_start(message: Message, state: FSMContext):
    entry_id = parse_id(message.text or "")
    if not entry_id:
        await message.answer("Usage: /edit ENTRY_ID")
        return
    scope_id, _ = scope_for(message)
    await state.clear()
    await state.update_data(entry_id=entry_id, scope_id=scope_id)
    await state.set_state(EditFlow.payload)
    await message.answer("Send the updated title on the first line and the new content on the following lines.")


@router.message(EditFlow.payload)
async def edit_payload(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if "\n" not in text:
        await message.answer("Please send two parts: title on the first line, then content on the next line.")
        return
    title, content = text.split("\n", 1)
    if not title.strip() or len(title.strip()) > MAX_TITLE_LENGTH or not content.strip() or len(content.strip()) > MAX_CONTENT_LENGTH:
        await message.answer("Invalid title/content length. Please try again.")
        return
    data = await state.get_data()
    result = await update_entry(data["scope_id"], data["entry_id"], message.from_user.id, title, content)
    await state.clear()
    if result.modified_count:
        await message.answer("✅ Entry updated.")
    else:
        await message.answer("Entry not found, not approved, or you are not its owner.")


@router.message(Command("delete"))
async def delete_command(message: Message):
    entry_id = parse_id(message.text or "")
    if not entry_id:
        await message.answer("Usage: /delete ENTRY_ID")
        return
    scope_id, _ = scope_for(message)
    result = await delete_entry(scope_id, entry_id, owner_id=message.from_user.id)
    if result.deleted_count:
        await message.answer("🗑 Entry deleted.")
    else:
        await message.answer("Entry not found or you are not its owner.")
