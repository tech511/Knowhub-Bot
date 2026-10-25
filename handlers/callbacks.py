from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from config import PAGE_SIZE
from database.repositories import scope_for, search_entries, get_entry, get_categories, stats, delete_entry
from keyboards.main_menu import main_menu, page_keyboard, categories_keyboard, entry_actions
from handlers.entries import SaveFlow, EditFlow

router = Router()


async def callback_scope(callback: CallbackQuery):
    if callback.message is None:
        return None
    if callback.message.chat.type == "private":
        return f"user:{callback.from_user.id}"
    return f"group:{callback.message.chat.id}"


@router.callback_query(F.data.startswith("menu:"))
async def menu_callback(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split(":", 1)[1]
    scope_id = await callback_scope(callback)
    if action == "search":
        await callback.message.answer("Use /search followed by a keyword, for example: /search python")
    elif action == "save":
        await state.clear()
        await state.set_state(SaveFlow.title)
        await callback.message.answer("Send a short title for the entry.")
    elif action == "categories":
        cats = await get_categories(scope_id)
        await callback.message.answer("Choose a category:", reply_markup=categories_keyboard(cats)) if cats else await callback.message.answer("No categories yet.")
    elif action == "stats":
        approved, pending, cat_count = await stats(scope_id)
        await callback.message.answer(f"📊 Approved: {approved}\nPending: {pending}\nCategories: {cat_count}")
    elif action == "mine":
        entries, total = await search_entries(scope_id, "", 0, PAGE_SIZE, owner_id=callback.from_user.id)
        await callback.message.answer("Your entries:", reply_markup=page_keyboard(entries, 0, total, PAGE_SIZE)) if entries else await callback.message.answer("No approved entries yet.")
    elif action == "help":
        await callback.message.answer("Use /save to add, /search keyword to find, /categories to browse, and /myentries to manage your entries.")
    await callback.answer()


@router.callback_query(F.data.startswith("page:"))
async def page_callback(callback: CallbackQuery):
    page = max(0, int(callback.data.split(":")[1]))
    scope_id = await callback_scope(callback)
    entries, total = await search_entries(scope_id, "", page, PAGE_SIZE)
    if not entries:
        await callback.answer("No more results.", show_alert=True)
        return
    await callback.message.edit_text(
        f"📚 Entries — page {page + 1} (total {total})",
        reply_markup=page_keyboard(entries, page, total, PAGE_SIZE),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("entry:"))
async def entry_callback(callback: CallbackQuery):
    entry_id = int(callback.data.split(":")[1])
    scope_id = await callback_scope(callback)
    entry = await get_entry(scope_id, entry_id)
    if not entry:
        await callback.answer("Entry not found or pending approval.", show_alert=True)
        return
    from html import escape
    text = (
        f"📌 <b>#{entry['entry_id']} — {escape(entry['title'])}</b>\n"
        f"Category: {escape(entry.get('category', 'general'))}\n"
        f"Tags: {escape(', '.join(entry.get('tags', [])) or 'none')}\n\n"
        f"{escape(entry['content'])}"
    )
    await callback.message.answer(text, reply_markup=entry_actions(entry_id, entry["owner_id"] == callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data.startswith("category:"))
async def category_callback(callback: CallbackQuery):
    category = callback.data.split(":", 1)[1]
    scope_id = await callback_scope(callback)
    entries, total = await search_entries(scope_id, category, 0, PAGE_SIZE)
    # Search is full-text-like substring matching; filter category exactly for this view.
    from database.mongo import get_db
    cursor = get_db().entries.find({"scope_id": scope_id, "status": "approved", "category": category}).sort("created_at", -1).limit(PAGE_SIZE)
    entries = await cursor.to_list(length=PAGE_SIZE)
    total = await get_db().entries.count_documents({"scope_id": scope_id, "status": "approved", "category": category})
    if entries:
        await callback.message.answer(f"📁 {category} ({total})", reply_markup=page_keyboard(entries, 0, total, PAGE_SIZE))
    else:
        await callback.message.answer("No entries in this category.")
    await callback.answer()


@router.callback_query(F.data.startswith("delete:"))
async def delete_button(callback: CallbackQuery):
    entry_id = int(callback.data.split(":")[1])
    scope_id = await callback_scope(callback)
    result = await delete_entry(scope_id, entry_id, owner_id=callback.from_user.id)
    await callback.message.answer("🗑 Deleted." if result.deleted_count else "Cannot delete this entry.")
    await callback.answer()


@router.callback_query(F.data.startswith("edit:"))
async def edit_button(callback: CallbackQuery, state: FSMContext):
    entry_id = int(callback.data.split(":")[1])
    scope_id = await callback_scope(callback)
    entry = await get_entry(scope_id, entry_id)
    if not entry or entry["owner_id"] != callback.from_user.id:
        await callback.answer("Only the entry owner can edit it.", show_alert=True)
        return
    await state.clear()
    await state.update_data(entry_id=entry_id, scope_id=scope_id)
    await state.set_state(EditFlow.payload)
    await callback.message.answer("Send updated title on the first line and content on the following lines.")
    await callback.answer()
