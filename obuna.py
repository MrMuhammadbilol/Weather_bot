import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

API_TOKEN = 'api_token'
OWM_API_KEY = 'weather_api'

# Bot va dispatcher ni yaratamiz
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Logging konfiguratsiyasi
logging.basicConfig(level=logging.INFO)
logging.info(f"Bot ishga tushdi: {API_TOKEN}")

# O'zbekiston viloyatlari
UZB_CITIES = [
    "Tashkent", "Namangan", "Andijan", "Fergana", "Samarkand", "Bukhara",
    "Navoiy", "Khorezm", "Surkhandarya", "Kashkadarya", "Sirdarya", "Jizzakh"
]


# OpenWeatherMap API orqali ob-havo ma'lumotlarini olish funksiyasi
def get_weather(city: str, days: int = 1):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&cnt=7&appid={OWM_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return "Ob-havo ma'lumotlarini olishda xatolik yuz berdi."

    forecasts = data['list'][:7]  # 7 kunlik ma'lumotlarni olish
    weather_info = f"{city} uchun 7 kunlik ob-havo:\n"

    for day in forecasts:
        date = day['dt_txt']
        temp = day['main']['temp']
        weather_desc = day['weather'][0]['description']
        humidity = day['main']['humidity']
        wind_speed = day['wind']['speed']

        weather_info += (
            f"\nSana: {date}\n"
            f"Harorat: {temp}°C\n"
            f"Tavsif: {weather_desc.capitalize()}\n"
            f"Namlik: {humidity}%\n"
            f"Shamol tezligi: {wind_speed} m/s\n"
        )
    return weather_info


# Start komandasi uchun handler
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    for city in UZB_CITIES:
        keyboard.add(InlineKeyboardButton(text=city, callback_data=f"weather_{city}"))

    await message.reply("Viloyatni tanlang:", reply_markup=keyboard)


# Ob-havo ma'lumotlarini olish uchun handler
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('weather_'))
async def process_callback_weather(callback_query: types.CallbackQuery):
    _, city = callback_query.data.split('_')
    weather_info = get_weather(city)
    await bot.send_message(callback_query.from_user.id, weather_info, parse_mode=ParseMode.HTML)
    await bot.answer_callback_query(callback_query.id)


if __name__ == "__main__":
    logging.info("Bot ishlayapti...")
    executor.start_polling(dp, skip_updates=True)
