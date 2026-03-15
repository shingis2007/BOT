from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import admin_main_menu, user_main_menu, cancel_kb
from database import add_tadbir, get_arizalar, get_murojaatlar, get_all_users
from config import ADMIN_IDS

router = Router()

def is_admin(user_id):
    return user_id in ADMIN_IDS

# States
class ElanState(StatesGroup):
    text = State()

class TadbirState(StatesGroup):
    nomi = State()
    sana = State()
    joy = State()
    tavsif = State()

# /admin buyrug'i
@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqi yo'q.")
        return
    await message.answer(
        "🔐 <b>Admin panelga xush kelibsiz!</b>",
        reply_markup=admin_main_menu(),
        parse_mode="HTML"
    )

# Foydalanuvchi menyusiga qaytish
@router.message(F.text == "🔙 Foydalanuvchi menyusi")
async def back_to_user(message: Message):
    await message.answer("Foydalanuvchi menyusi:", reply_markup=user_main_menu())

# E'lon yuborish
@router.message(F.text == "📤 E'lon yuborish")
async def elan_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(ElanState.text)
    await message.answer(
        "📤 <b>Barcha foydalanuvchilarga e'lon yuboring:</b>\n\nMatnni kiriting:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )

@router.message(ElanState.text)
async def elan_send(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return

    users = get_all_users()
    yuborildi = 0
    xato = 0

    for user_id in users.keys():
        try:
            await message.bot.send_message(
                int(user_id),
                f"📢 <b>Yoshlar Ittifoqi e'loni:</b>\n\n{message.text}",
                parse_mode="HTML"
            )
            yuborildi += 1
        except:
            xato += 1

    await state.clear()
    await message.answer(
        f"✅ E'lon yuborildi!\n\n"
        f"✔️ Muvaffaqiyatli: {yuborildi} ta\n"
        f"❌ Xatolik: {xato} ta",
        reply_markup=admin_main_menu()
    )

# Tadbir qo'shish
@router.message(F.text == "📅 Tadbir qo'shish")
async def tadbir_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(TadbirState.nomi)
    await message.answer("📅 Tadbir nomini kiriting:", reply_markup=cancel_kb())

@router.message(TadbirState.nomi)
async def tadbir_nomi(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return
    await state.update_data(nomi=message.text)
    await state.set_state(TadbirState.sana)
    await message.answer("📆 Tadbir sanasini kiriting (masalan: 20-mart 2025):")

@router.message(TadbirState.sana)
async def tadbir_sana(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return
    await state.update_data(sana=message.text)
    await state.set_state(TadbirState.joy)
    await message.answer("📍 Tadbir o'tkaziladigan joyni kiriting:")

@router.message(TadbirState.joy)
async def tadbir_joy(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return
    await state.update_data(joy=message.text)
    await state.set_state(TadbirState.tavsif)
    await message.answer("📝 Tadbir haqida qisqacha tavsif kiriting:")

@router.message(TadbirState.tavsif)
async def tadbir_save(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return
    data = await state.get_data()
    add_tadbir(data["nomi"], data["sana"], data["joy"], message.text)
    await state.clear()
    await message.answer(
        f"✅ Tadbir qo'shildi!\n\n"
        f"🎉 <b>{data['nomi']}</b>\n"
        f"📆 {data['sana']} | 📍 {data['joy']}",
        reply_markup=admin_main_menu(),
        parse_mode="HTML"
    )

# Arizalar ro'yxati
@router.message(F.text == "📋 Arizalar")
async def arizalar(message: Message):
    if not is_admin(message.from_user.id):
        return
    arizalar_list = get_arizalar()
    if not arizalar_list:
        await message.answer("📋 Hozircha ariza yo'q.")
        return
    text = f"📋 <b>Jami arizalar: {len(arizalar_list)} ta</b>\n\n"
    for a in arizalar_list[-10:]:  # Oxirgi 10 ta
        text += f"#{a['id']} | {a['full_name']}\n"
        text += f"📅 {a['date']}\n"
        text += f"📄 {a['text'][:100]}...\n\n"
    await message.answer(text, parse_mode="HTML")

# Murojaatlar ro'yxati
@router.message(F.text == "📨 Murojaatlar")
async def murojaatlar(message: Message):
    if not is_admin(message.from_user.id):
        return
    murojaatlar_list = get_murojaatlar()
    if not murojaatlar_list:
        await message.answer("📨 Hozircha murojaat yo'q.")
        return
    text = f"📨 <b>Jami murojaatlar: {len(murojaatlar_list)} ta</b>\n\n"
    for m in murojaatlar_list[-10:]:
        text += f"#{m['id']} | {m['full_name']}\n"
        text += f"📅 {m['date']}\n"
        text += f"💬 {m['text'][:100]}...\n\n"
    await message.answer(text, parse_mode="HTML")

# Foydalanuvchilar soni
@router.message(F.text == "👥 Foydalanuvchilar")
async def foydalanuvchilar(message: Message):
    if not is_admin(message.from_user.id):
        return
    users = get_all_users()
    await message.answer(
        f"👥 <b>Foydalanuvchilar soni: {len(users)} ta</b>",
        parse_mode="HTML"
    )
