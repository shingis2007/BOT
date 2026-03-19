from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import admin_main_menu, user_main_menu, cancel_kb
from database import (add_tadbir, get_murojaatlar, get_all_users,
                      get_qatnashuvchilar, get_tadbirlar,
                      add_kengash_azosi, get_kengash_azolari, delete_kengash_azosi)
from config import ADMIN_IDS

router = Router()

def is_admin(user_id):
    return user_id in ADMIN_IDS

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

# /admin
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
    await message.answer("Foydalanuvchi menyusi:", reply_markup=user_main_menu())

# E'lon yuborish
@router.message(F.text == "📤 E'lon yuborish")
async def elan_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(ElanState.text)
    await message.answer("📤 Barcha foydalanuvchilarga e'lon matni yozing:", reply_markup=cancel_kb())

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
    tadbir_id = add_tadbir(data["nomi"], data["sana"], data["joy"], message.text)
    await state.clear()
    await message.answer(
        f"✅ Tadbir qo'shildi!\n\n🎉 <b>{data['nomi']}</b>\n📆 {data['sana']} | 📍 {data['joy']}",
        reply_markup=admin_main_menu(),
        parse_mode="HTML"
    )

# Murojaatlar
@router.message(F.text == "📨 Murojaatlar")
async def murojaatlar(message: Message):
    if not is_admin(message.from_user.id):
        return
    murojaatlar_list = get_murojaatlar()
    if not murojaatlar_list:
        await message.answer("📨 Hozircha murojaat yo'q.")
        return
    text = f"📨 <b>Jami: {len(murojaatlar_list)} ta murojaat</b>\n\n"
    for m in murojaatlar_list[-10:]:
        uname = f"@{m.get('username')}" if m.get('username') else "username yo'q"
        text += f"#{m['id']} | {m['full_name']} ({uname})\n"
        text += f"📅 {m['date']}\n"
        text += f"💬 {m['text'][:100]}\n"
        text += f"📨 /javob_{m['user_id']}\n\n"
    await message.answer(text, parse_mode="HTML")

# Qatnashuvchilar
@router.message(F.text == "🙋 Qatnashuvchilar")
async def qatnashuvchilar(message: Message):
    if not is_admin(message.from_user.id):
        return
    tadbirlar = get_tadbirlar()
    barcha = get_qatnashuvchilar()
    if not barcha:
        await message.answer("🙋 Hozircha hech kim qatnashishini bildirmagan.")
        return
    for t in tadbirlar:
        qlist = barcha.get(str(t['id']), [])
        if not qlist:
            continue
        text = f"📅 <b>{t['nomi']}</b> — {len(qlist)} ta qatnashuvchi\n\n"
        for i, q in enumerate(qlist, 1):
            uname = f"@{q['username']}" if q.get('username') else "username yo'q"
            telefon = q.get('telefon', 'kiritilmagan')
            text += f"{i}. {q['full_name']} ({uname}) — 📱 {telefon}\n"
        await message.answer(text, parse_mode="HTML")

# Foydalanuvchilar
@router.message(F.text == "👥 Foydalanuvchilar")
async def foydalanuvchilar(message: Message):
    if not is_admin(message.from_user.id):
        return
    users = get_all_users()
    await message.answer(f"👥 <b>Foydalanuvchilar soni: {len(users)} ta</b>", parse_mode="HTML")

# A'zo qo'shish
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
    await message.answer("💼 Lavozimini kiriting (masalan: Raisi, Kotibi, Xazinachisi):")

@router.message(AzoState.lavozim)
async def azo_lavozim(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return
    await state.update_data(lavozim=message.text)
    await state.set_state(AzoState.username)
    await message.answer("🔗 Telegram username kiriting (masalan: @username):")

@router.message(AzoState.username)
async def azo_username(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return
    await state.update_data(username=message.text)
    await state.set_state(AzoState.photo)
    await message.answer("📸 A'zoning rasmini yuboring (rasm bo'lmasa 'O'tkazib yuborish' yozing):")

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
    add_kengash_azosi(data["ism"], data["lavozim"], data["username"], photo_id)
    await state.clear()
    await message.answer(
        f"✅ Kengash a'zosi qo'shildi!\n\n"
        f"👤 <b>{data['ism']}</b>\n"
        f"💼 {data['lavozim']}\n"
        f"🔗 {data['username']}\n"
        f"📸 Rasm: {'✅ qo\'shildi' if photo_id else '❌ yo\'q'}",
        reply_markup=admin_main_menu(),
        parse_mode="HTML"
    )

# A'zoni o'chirish
@router.message(F.text == "🗑 A'zoni o'chirish")
async def azo_ochirish(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    azolar = get_kengash_azolari()
    if not azolar:
        await message.answer("👥 Hozircha kengash a'zolari yo'q.")
        return
    text = "🗑 <b>Qaysi a'zoni o'chirmoqchisiz?</b>\n\nID ni yozing:\n\n"
    for a in azolar:
        text += f"ID: <code>{a['id']}</code> — {a['ism']} ({a['lavozim']})\n"
    await state.set_state(OchirishState.azo_id)
    await message.answer(text, reply_markup=cancel_kb(), parse_mode="HTML")

@router.message(OchirishState.azo_id)
async def azo_ochirish_confirm(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return
    try:
        azo_id = int(message.text)
        delete_kengash_azosi(azo_id)
        await state.clear()
        await message.answer(f"✅ #{azo_id} ID li a'zo o'chirildi.", reply_markup=admin_main_menu())
    except:
        await message.answer("❌ Noto'g'ri ID. Qaytadan kiriting:")

# Javob berish
@router.message(F.text.startswith("/javob_"))
async def javob_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        user_id = int(message.text.split("_")[1])
        await state.set_state(JavobState.text)
        await state.update_data(user_id=user_id)
        await message.answer(
            f"✏️ Foydalanuvchi <code>{user_id}</code> ga javob yozing:",
            reply_markup=cancel_kb(),
            parse_mode="HTML"
        )
    except:
        await message.answer("❌ Xatolik.")

@router.message(JavobState.text)
async def javob_send(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
        return
    data = await state.get_data()
    try:
        await message.bot.send_message(
            data["user_id"],
            f"📬 <b>Yoshlar Ittifoqidan javob:</b>\n\n{message.text}",
            parse_mode="HTML"
        )
        await state.clear()
        await message.answer("✅ Javob yuborildi!", reply_markup=admin_main_menu())
    except:
        await state.clear()
        await message.answer("❌ Foydalanuvchiga xabar yuborib bo'lmadi.", reply_markup=admin_main_menu())
