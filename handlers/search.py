from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.repositories import scope_for, search_entries, get_categories, stats
from keyboards.main_menu import page_keyboard, categories_keyboard
from config import PAGE_SIZE

router = Router()


@router.message(Command("search"))
async def search_command(message: Message):
    query = message.text.partition(" ")[2].strip() if message.text else ""
    if not query:
        await message.answer("Usage: /search keyword")
        return
    scope_id, _ = scope_for(message)
    entries, total = await search_entries(scope_id, query, 0, PAGE_SIZE)
    if not entries:
        await message.answer("No approved entries found. Try another keyword.")
        return
    await message.answer(f"🔎 Results for <b>{query[:100]}</b> — {total} found:", reply_markup=page_keyboard(entries, 0, total, PAGE_SIZE))


@router.message(Command("categories"))
async def categories_command(message: Message):
    scope_id, _ = scope_for(message)
    categories = await get_categories(scope_id)
    kb = categories_keyboard(categories)
    if not kb:
        await message.answer("No categories yet. Save an entry first with /save.")
    else:
        await message.answer("Choose a category:", reply_markup=kb)


@router.message(Command("stats"))
async def stats_command(message: Message):
    scope_id, _ = scope_for(message)
    approved, pending, count_categories = await stats(scope_id)
    await message.answer(
        f"📊 <b>KnowHub statistics</b>\n\n"
        f"Approved entries: {approved}\nPending entries: {pending}\nCategories: {count_categories}"
    )
