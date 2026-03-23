from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import admin_main_menu, user_main_menu, cancel_kb
from database import (
    add_tadbir, get_murojaatlar, get_all_users,
    get_qatnashuvchilar, get_tadbirlar,
    add_kengash_azosi, get_kengash_azolari, delete_kengash_azosi
)
from config import ADMIN_IDS

router = Router()


def is_admin(user_id):
    return user_id in ADMIN_IDS


# ================= STATES =================

class ElanState(StatesGroup):
    text = State()


class TadbirState(StatesGroup):
    nomi = State()
    sana = State()
    joy = State()
    tavsif = State()


class JavobState(StatesGroup):
    user_id = State()
    text = State()


class AzoState(StatesGroup):
    ism = State()
    lavozim = State()
    username = State()
    photo = State()


class OchirishState(StatesGroup):
    azo_id = State()


# ================= ADMIN PANEL =================

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


@router.message(F.text == "🔙 Foydalanuvchi menyusi")
async def back_to_user(message: Message):
    await message.answer(
        "Foydalanuvchi menyusi:",
        reply_markup=user_main_menu()
    )


# ================= ELON =================

@router.message(F.text == "📤 E'lon yuborish")
async def elan_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.set_state(ElanState.text)
    await message.answer(
        "📤 Barcha foydalanuvchilarga e'lon matni yozing:",
        reply_markup=cancel_kb()
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
        f"✅ E'lon yuborildi!\n✔️ {yuborildi} ta\n❌ {xato} ta xatolik",
        reply_markup=admin_main_menu()
    )


# ================= TADBIR =================

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

    await message.answer("📆 Tadbir sanasini kiriting:")


@router.message(TadbirState.sana)
async def tadbir_sana(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return

    await state.update_data(sana=message.text)
    await state.set_state(TadbirState.joy)

    await message.answer("📍 Tadbir joyini kiriting:")


@router.message(TadbirState.joy)
async def tadbir_joy(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return

    await state.update_data(joy=message.text)
    await state.set_state(TadbirState.tavsif)

    await message.answer("📝 Tadbir tavsifini kiriting:")


@router.message(TadbirState.tavsif)
async def tadbir_save(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return

    data = await state.get_data()

    add_tadbir(
        data["nomi"],
        data["sana"],
        data["joy"],
        message.text
    )

    await state.clear()

    await message.answer(
        f"✅ Tadbir qo'shildi!\n\n🎉 <b>{data['nomi']}</b>\n📆 {data['sana']} | 📍 {data['joy']}",
        reply_markup=admin_main_menu(),
        parse_mode="HTML"
    )


# ================= AZO QO‘SHISH =================

@router.message(F.text == "➕ Kengash a'zosi qo'shish")
async def azo_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.set_state(AzoState.ism)
    await message.answer("👤 A'zoning to'liq ismini kiriting:", reply_markup=cancel_kb())


@router.message(AzoState.ism)
async def azo_ism(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return

    await state.update_data(ism=message.text)
    await state.set_state(AzoState.lavozim)

    await message.answer("💼 Lavozimini kiriting:")


@router.message(AzoState.lavozim)
async def azo_lavozim(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return

    await state.update_data(lavozim=message.text)
    await state.set_state(AzoState.username)

    await message.answer("🔗 Username kiriting:")


@router.message(AzoState.username)
async def azo_username(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return

    await state.update_data(username=message.text)
    await state.set_state(AzoState.photo)

    await message.answer("📸 Rasm yuboring yoki 'O'tkazib yuborish' yozing:")


@router.message(AzoState.photo)
async def azo_photo(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return

    data = await state.get_data()

    photo_id = None
    if message.photo:
        photo_id = message.photo[-1].file_id

    add_kengash_azosi(
        data["ism"],
        data["lavozim"],
        data["username"],
        photo_id
    )

    rasm_status = "✅ qo'shildi" if photo_id else "❌ yo'q"

    text = (
        f"✅ Kengash a'zosi qo'shildi!\n\n"
        f"👤 <b>{data['ism']}</b>\n"
        f"💼 {data['lavozim']}\n"
        f"🔗 {data['username']}\n"
        f"📸 Rasm: {rasm_status}"
    )

    await state.clear()

    await message.answer(
        text,
        reply_markup=admin_main_menu(),
        parse_mode="HTML"
    )
