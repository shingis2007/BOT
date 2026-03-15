from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Foydalanuvchi asosiy menyu
def user_main_menu():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📢 E'lonlar"), KeyboardButton(text="📅 Tadbirlar")],
        [KeyboardButton(text="📝 Ariza yuborish"), KeyboardButton(text="🎧 Murojaat")],
        [KeyboardButton(text="ℹ️ Biz haqimizda")]
    ], resize_keyboard=True)
    return kb

# Admin asosiy menyu
def admin_main_menu():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📤 E'lon yuborish"), KeyboardButton(text="📅 Tadbir qo'shish")],
        [KeyboardButton(text="📋 Arizalar"), KeyboardButton(text="📨 Murojaatlar")],
        [KeyboardButton(text="👥 Foydalanuvchilar"), KeyboardButton(text="🔙 Foydalanuvchi menyusi")]
    ], resize_keyboard=True)
    return kb

# Bekor qilish tugmasi
def cancel_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="❌ Bekor qilish")]
    ], resize_keyboard=True)
    return kb
