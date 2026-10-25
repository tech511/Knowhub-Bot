from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from keyboards.main_menu import main_menu

router = Router()

WELCOME = (
    "👋 <b>Welcome to KnowHub!</b>\n\n"
    "Save useful text and links, organize community knowledge, and find it later.\n\n"
    "In a private chat, entries are your personal library. In a group, entries are shared with that group."
)


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(WELCOME, reply_markup=main_menu())


@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "<b>KnowHub Help</b>\n\n"
        "/save — save a title and text/link\n"
        "/search keyword — search entries\n"
        "/categories — browse categories\n"
        "/myentries — list your entries\n"
        "/edit ID — edit one of your entries\n"
        "/delete ID — delete one of your entries\n"
        "/stats — show library statistics\n"
        "/settings — show group settings\n\n"
        "In groups, new entries are pending until an admin approves them."
    )
