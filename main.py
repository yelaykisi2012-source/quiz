import asyncio
import os
import random
import sqlite3
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import buttons
# questions faylidan har ikkala ro'yxatni import qilamiz
from questions import quiz_data, js_quiz_data

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# --- BAZA ---
conn = sqlite3.connect('quiz_bot.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, score INTEGER DEFAULT 0)')
conn.commit()

last_explanation = {}

# --- HANDLERLAR ---

@dp.message(Command("start"))
async def start(message: types.Message):
    cursor.execute('INSERT OR IGNORE INTO users (user_id, score) VALUES (?, 0)', (message.from_user.id,))
    conn.commit()
    await message.answer(
        "Qaysi yo'nalish bo'yicha bilimingizni sinaymiz?",
        reply_markup=buttons.get_main_menu()
    )

# --- Python Savollari ---
@dp.message(F.text == "🐍 Python savol")
async def send_python_quiz(message: types.Message):
    q = random.choice(quiz_data)
    last_explanation[message.from_user.id] = q['explanation']
    await message.answer_poll(
        question=f"Python: Bu kod nima natija beradi?\n\n{q['code']}",
        options=q['options'],
        type='quiz',
        correct_option_id=q['correct_index'],
        explanation=q['explanation'],
        is_anonymous=False,
        reply_markup=buttons.get_quiz_info()
    )

# --- JavaScript Savollari ---
@dp.message(F.text == "🌐 JavaScript savol")
async def send_js_quiz(message: types.Message):
    q = random.choice(js_quiz_data)
    last_explanation[message.from_user.id] = q['explanation']
    await message.answer_poll(
        question=f"JS: Bu kod nima natija beradi?\n\n{q['code']}",
        options=q['options'],
        type='quiz',
        correct_option_id=q['correct_index'],
        explanation=q['explanation'],
        is_anonymous=False,
        reply_markup=buttons.get_quiz_info()
    )

@dp.poll_answer()
async def handle_poll_answer(poll_answer: types.PollAnswer):
    # Har qanday javob uchun ball qo'shish (Xohlasangiz faqat to'g'ri javobga sozlash mumkin)
    cursor.execute('UPDATE users SET score = score + 1 WHERE user_id = ?', (poll_answer.user.id,))
    conn.commit()

@dp.message(F.text == "📊 Мой рейтинг")
async def show_rating(message: types.Message):
    cursor.execute('SELECT score FROM users WHERE user_id = ?', (message.from_user.id,))
    result = cursor.fetchone()
    score = result[0] if result else 0
    await message.answer(f"🏆 Sizning balingiz: {score}")

@dp.callback_query(F.data == "explain")
async def explain_handler(callback: types.CallbackQuery):
    explanation = last_explanation.get(callback.from_user.id, "Izoh topilmadi.")
    await callback.answer(text=explanation, show_alert=True)

@dp.message(F.text == "⚙️ Помощь")
async def help_cmd(message: types.Message):
    await message.answer("Tugmalarni bosing va bilimingizni sinang!")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
