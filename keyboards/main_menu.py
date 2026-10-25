from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔎 Search", callback_data="menu:search"),
         InlineKeyboardButton(text="➕ Save entry", callback_data="menu:save")],
        [InlineKeyboardButton(text="📂 Categories", callback_data="menu:categories"),
         InlineKeyboardButton(text="📊 Statistics", callback_data="menu:stats")],
        [InlineKeyboardButton(text="📚 My entries", callback_data="menu:mine"),
         InlineKeyboardButton(text="❔ Help", callback_data="menu:help")],
    ])


def page_keyboard(entries, page, total, page_size=5):
    rows = []
    for entry in entries:
        title = entry.get("title", "Untitled")[:45]
        rows.append([InlineKeyboardButton(
            text=f"#{entry['entry_id']} · {title}",
            callback_data=f"entry:{entry['entry_id']}"
        )])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"page:{page-1}"))
    if (page + 1) * page_size < total:
        nav.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"page:{page+1}"))
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def categories_keyboard(categories):
    rows = [[InlineKeyboardButton(text=f"📁 {cat[:45]}", callback_data=f"category:{cat}")]
            for cat in categories[:50]]
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None


def entry_actions(entry_id, owner=False):
    rows = []
    if owner:
        rows.append([
            InlineKeyboardButton(text="✏️ Edit", callback_data=f"edit:{entry_id}"),
            InlineKeyboardButton(text="🗑 Delete", callback_data=f"delete:{entry_id}"),
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None
