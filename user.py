from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import user_main_menu, cancel_kb, qatnashish_kb
from database import register_user, add_murojaat, get_tadbirlar, add_qatnashuvchi, get_kengash_azolari
from config import ADMIN_IDS

router = Router()

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
        "📢 <b>So'nggi e'lonlar</b>\n\nHozircha yangi e'lon yo'q. Kuzatib boring!",
        parse_mode="HTML"
    )

# Tadbirlar
@router.message(F.text == "📅 Tadbirlar")
async def tadbirlar(message: Message):
    tadbirlar_list = get_tadbirlar()
    if not tadbirlar_list:
        await message.answer("📅 Hozircha rejalashtirilgan tadbir yo'q.")
        return
    for t in tadbirlar_list:
        text = (
            f"📅 <b>{t['nomi']}</b>\n"
            f"📆 Sana: {t['sana']}\n"
            f"📍 Joy: {t['joy']}\n"
            f"📝 {t['tavsif']}"
        )
        await message.answer(text, reply_markup=qatnashish_kb(t['id']), parse_mode="HTML")

# Qatnashish callback
@router.callback_query(F.data.startswith("qatnash_"))
async def qatnash(callback: CallbackQuery):
    tadbir_id = int(callback.data.split("_")[1])
    user = callback.from_user
    natija = add_qatnashuvchi(tadbir_id, user.id, user.full_name, user.username)
    tadbirlar = get_tadbirlar()
    tadbir = next((t for t in tadbirlar if t['id'] == tadbir_id), None)
    tadbir_nomi = tadbir['nomi'] if tadbir else f"#{tadbir_id}"
    if natija:
        await callback.answer("✅ Qatnashishingiz ro'yxatga olindi!", show_alert=True)
        for admin_id in ADMIN_IDS:
            try:
                await callback.bot.send_message(
                    admin_id,
                    f"🙋 <b>Yangi qatnashuvchi!</b>\n\n"
                    f"📅 Tadbir: <b>{tadbir_nomi}</b>\n"
                    f"👤 Kim: {user.full_name}\n"
                    f"🔗 Nickname: @{user.username or 'username yoq'}\n"
                    f"🆔 ID: <code>{user.id}</code>",
                    parse_mode="HTML"
                )
            except:
                pass
    else:
        await callback.answer("ℹ️ Siz allaqachon ro'yxatga olindingiz!", show_alert=True)

# Murojaat
@router.message(F.text == "📨 Murojaat")
async def murojaat_start(message: Message, state: FSMContext):
    await state.set_state(MurojaatState.text)
    await message.answer(
        "📨 <b>Murojaat yuborish</b>\n\n"
        "Ariza, savol yoki muammoingizni yozing.\n"
        "Tez orada javob beramiz!",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )

@router.message(MurojaatState.text)
async def murojaat_save(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=user_main_menu())
        return
    add_murojaat(message.from_user.id, message.from_user.full_name, message.from_user.username, message.text)
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                admin_id,
                f"📨 <b>Yangi murojaat!</b>\n\n"
                f"👤 Kim: {message.from_user.full_name}\n"
                f"🔗 Nickname: @{message.from_user.username or 'username yoq'}\n"
                f"🆔 ID: <code>{message.from_user.id}</code>\n\n"
                f"💬 Murojaat:\n{message.text}\n\n"
                f"📨 Javob: /javob_{message.from_user.id}",
                parse_mode="HTML"
            )
        except:
            pass
    await state.clear()
    await message.answer(
        "✅ Murojaatingiz qabul qilindi!\n24 soat ichida javob beramiz.",
        reply_markup=user_main_menu()
    )

# Kengash azolari
@router.message(F.text == "👥 Kengash azolari")
async def kengash(message: Message):
    azolar = get_kengash_azolari()
    if not azolar:
        await message.answer(
            "👥 <b>Kengash azolari</b>\n\nHozircha ma'lumot kiritilmagan.",
            parse_mode="HTML"
        )
        return
    await message.answer("👥 <b>Yoshlar Ittifoqi Kengash Azolari</b>", parse_mode="HTML")
    for a in azolar:
        text = (
            f"💼 <b>{a['lavozim']}</b>\n"
            f"👤 {a['ism']}\n"
            f"🔗 {a['username']}"
        )
        if a.get('photo_id'):
            await message.answer_photo(
                photo=a['photo_id'],
                caption=text,
                parse_mode="HTML"
            )
        else:
            await message.answer(text, parse_mode="HTML")

# Biz haqimizda
@router.message(F.text == "ℹ️ Biz haqimizda")
async def haqimizda(message: Message):
    await message.answer(
        "🎓 <b>Yoshlar Ittifoqi haqida</b>\n\n"
        "Biz universiteti talabalari hayotini yanada mazmunli qilish uchun ishlaydi.\n\n"
        "🎯 Maqsadimiz: Yoshlarni birlashtirish, rivojlantirish va qo'llab-quvvatlash.\n\n"
        "📞 Bog'lanish: @yoshlar_admin",
        parse_mode="HTML"
    )
