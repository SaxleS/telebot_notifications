import base64

from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.bot.keyboards import main_menu


from datetime import datetime


router = Router()

@router.message(F.text == "/help")
async def start_command(message: Message):
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=main_menu)

def register_handlers() -> Router:
    return router
