import os
import django
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from asgiref.sync import sync_to_async
from dotenv import load_dotenv


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from booking.models import Client, Service, Booking

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())



class BookingState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_service = State()
    waiting_for_date = State()


@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    client = await sync_to_async(Client.objects.filter(telegram_id=user_id).first)()

    if not client:
        btn = KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)
        kb = ReplyKeyboardMarkup(keyboard=[[btn]], resize_keyboard=True)
        await message.answer("Здравствуйте! Отправьте ваш номер телефона для регистрации:", reply_markup=kb)
        await state.set_state(BookingState.waiting_for_phone)
    else:
        await show_services(message, state)


@dp.message(BookingState.waiting_for_phone, F.contact)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone, full_name=message.from_user.full_name)
    await message.answer("Отлично! Теперь введите ваш Email адрес (для отправки чека):",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(BookingState.waiting_for_email)


@dp.message(BookingState.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text
    data = await state.get_data()

    # Сохраняем клиента в БД
    client, _ = await sync_to_async(Client.objects.get_or_create)(
        telegram_id=message.from_user.id,
        defaults={
            'full_name': data['full_name'],
            'phone': data['phone'],
            'email': email
        }
    )
    await message.answer("Регистрация завершена!")
    await show_services(message, state)


async def show_services(message: types.Message, state: FSMContext):
    services = await sync_to_async(list)(Service.objects.all())
    if not services:
        await message.answer("К сожалению, доступных услуг пока нет.")
        return

    buttons = []
    for s in services:
        buttons.append([InlineKeyboardButton(text=f"{s.name} - {s.price} сум", callback_data=f"service_{s.id}")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выберите услугу для записи:", reply_markup=kb)
    await state.set_state(BookingState.waiting_for_service)


@dp.callback_query(BookingState.waiting_for_service, F.data.startswith("service_"))
async def process_service(callback: types.CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split("_")[1])
    await state.update_data(service_id=service_id)

    await callback.message.answer(
        "Введите дату и время записи в формате `ГГГГ-ММ-ДД ЧЧ:ММ` (например: 2026-09-20 15:00):")
    await state.set_state(BookingState.waiting_for_date)
    await callback.answer()


@dp.message(BookingState.waiting_for_date)
async def process_date(message: types.Message, state: FSMContext):
    try:
        booking_dt = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        data = await state.get_data()

        client = await sync_to_async(Client.objects.get)(telegram_id=message.from_user.id)
        service = await sync_to_async(Service.objects.get)(id=data['service_id'])


        booking = await sync_to_async(Booking.objects.create)(
            client=client,
            service=service,
            booking_date=booking_dt
        )

        await message.answer(
            f"✅ Вы успешно записаны!\n\nУслуга: {service.name}\nДата: {booking_dt.strftime('%d.%m.%Y %H:%M')}")
        await state.clear()
    except ValueError:
        await message.answer("Неверный формат даты. Попробуйте еще раз (например: 2026-09-20 15:00):")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())