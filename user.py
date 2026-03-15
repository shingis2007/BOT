from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import user_main_menu, cancel_kb
from database import register_user, add_ariza, add_murojaat, get_tadbirlar
from config import ADMIN_IDS

router = Router()

# States
class ArizaState(StatesGroup):
    text = State()

class MurojaatState(StatesGroup):
    text = State()

# /start
@router.message(CommandStart())
async def start(message: Message):
    register_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    await message.answer(
        f"👋 Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
        "🎓 <b>Universitetdagi Yoshlar Ittifoqi</b> botiga xush kelibsiz!\n\n"
        "Quyidagi xizmatlardan foydalanishingiz mumkin:",
        reply_markup=user_main_menu(),
        parse_mode="HTML"
    )

# E'lonlar
@router.message(F.text == "📢 E'lonlar")
async def elanlar(message: Message):
    await message.answer(
        "📢 <b>So'nggi e'lonlar</b>\n\n"
        "Hozircha yangi e'lon yo'q. Kuzatib boring!",
        parse_mode="HTML"
    )

# Tadbirlar
@router.message(F.text == "📅 Tadbirlar")
async def tadbirlar(message: Message):
    tadbirlar_list = get_tadbirlar()
    if not tadbirlar_list:
        await message.answer("📅 Hozircha rejalashtirilgan tadbir yo'q.")
        return
    text = "📅 <b>Kelgusi tadbirlar:</b>\n\n"
    for t in tadbirlar_list:
        text += f"🔸 <b>{t['nomi']}</b>\n"
        text += f"   📆 Sana: {t['sana']}\n"
        text += f"   📍 Joy: {t['joy']}\n"
        text += f"   📝 {t['tavsif']}\n\n"
    await message.answer(text, parse_mode="HTML")

# Ariza yuborish
@router.message(F.text == "📝 Ariza yuborish")
async def ariza_start(message: Message, state: FSMContext):
    await state.set_state(ArizaState.text)
    await message.answer(
        "📝 <b>Ariza yuborish</b>\n\n"
        "Arizangizni yozing (to'liq isming, talaba raqamingiz va maqsadingizni kiriting):",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )

@router.message(ArizaState.text)
async def ariza_save(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=user_main_menu())
        return

    add_ariza(message.from_user.id, message.from_user.full_name, message.text)

    # Adminlarga xabar
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                admin_id,
                f"📝 <b>Yangi ariza!</b>\n\n"
                f"👤 Kim: {message.from_user.full_name} (@{message.from_user.username or 'username yoq'})\n"
                f"🆔 ID: <code>{message.from_user.id}</code>\n\n"
                f"📄 Ariza:\n{message.text}",
                parse_mode="HTML"
            )
        except:
            pass

    await state.clear()
    await message.answer(
        "✅ Arizangiz qabul qilindi! Tez orada javob beramiz.",
        reply_markup=user_main_menu()
    )

# Murojaat
@router.message(F.text == "🎧 Murojaat")
async def murojaat_start(message: Message, state: FSMContext):
    await state.set_state(MurojaatState.text)
    await message.answer(
        "🎧 <b>Murojaat yuborish</b>\n\n"
        "Savolingiz yoki muammongizni yozing:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )

@router.message(MurojaatState.text)
async def murojaat_save(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=user_main_menu())
        return

    add_murojaat(message.from_user.id, message.from_user.full_name, message.text)

    # Adminlarga xabar
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                admin_id,
                f"🎧 <b>Yangi murojaat!</b>\n\n"
                f"👤 Kim: {message.from_user.full_name} (@{message.from_user.username or 'username yoq'})\n"
                f"🆔 ID: <code>{message.from_user.id}</code>\n\n"
                f"💬 Murojaat:\n{message.text}",
                parse_mode="HTML"
            )
        except:
            pass

    await state.clear()
    await message.answer(
        "✅ Murojaatingiz qabul qilindi! 24 soat ichida javob beramiz.",
        reply_markup=user_main_menu()
    )

# Biz haqimizda
@router.message(F.text == "ℹ️ Biz haqimizda")
async def haqimizda(message: Message):
    await message.answer(
        "🎓 <b>Yoshlar Ittifoqi haqida</b>\n\n"
        "Biz universiteti talabalari hayotini yanada mazmunli qilish uchun ishlaydi.\n\n"
        "🎯 Maqsadimiz: Yoshlarni birlashtirish, rivojlantirish va qo'llab-quvvatlash.\n\n"
        "📞 Bog'lanish uchun: @yoshlar_admin",
        parse_mode="HTML"
    )
