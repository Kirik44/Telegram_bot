from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from bs4 import BeautifulSoup
from loguru import logger
import datetime
import requests
import sqlite3


bot = Bot(token="Token")
dp = Dispatcher(bot)


dbSQL = sqlite3.connect('Course.db', check_same_thread=False)
sql = dbSQL.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS course(
    requestTime TEXT,
    UsdRub TEXT,
    EurRub TEXT,
    BtnUsd TEXT,
    BtnRub TEXT,
    EthUsd TEXT,
    EthRub TEXT
)""")
dbSQL.commit()


USD_RUB = 'https://www.google.com/search?client=opera&q=dollar&sourceid=opera&ie=UTF-8&oe=UTF-8'
EUR_RUB = 'https://www.google.com/search?client=opera&q=евро+в+рублях&sourceid=opera&ie=UTF-8&oe=UTF-8'
BTN_USD = 'https://www.google.com/search?client=opera&q=биткоин+в+долларах&sourceid=opera&ie=UTF-8&oe=UTF-8'
BTN_RUB = 'https://www.google.com/search?client=opera&q=биткоин+в+рубли&sourceid=opera&ie=UTF-8&oe=UTF-8'
ETH_USD = 'https://www.google.com/search?client=opera&q=eth+в+доллары&sourceid=opera&ie=UTF-8&oe=UTF-8'
ETH_RUB = 'https://www.google.com/search?client=opera&q=1+eth+в+рублях&sourceid=opera&ie=UTF-8&oe=UTF-8'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/90.0.4430.212 Safari/537.36 OPR/76.0.4017.177'}


def Parsing(Currency):
    full_page = requests.get(Currency, headers=headers)
    soup = BeautifulSoup(full_page.content, 'html.parser')
    convert = soup.findAll("span", {"class": "DFlfde SwHCTb", "data-precision": "2"})

    requestTime = datetime.datetime.now().strftime("%H:%M")
    course = convert[0].text
    return requestTime, course


def ToInt(Value):
    Value = Value.split(",")
    return Value[0]


def DataRecording():
    Request = Parsing(USD_RUB)
    requestTime = Request[0]
    UsdRub = Request[1]
    EurRub = Parsing(EUR_RUB)[1]
    BtnUsd = ToInt(Parsing(BTN_USD)[1])
    BtnRub = ToInt(Parsing(BTN_RUB)[1])
    EthUsd = ToInt(Parsing(ETH_USD)[1])
    EthRub = ToInt(Parsing(ETH_RUB)[1])

    sql.execute(f"INSERT INTO course VALUES (?, ?, ?, ?, ?, ?, ?)", (str(requestTime), UsdRub, EurRub, BtnUsd, BtnRub,
                                                                     EthUsd, EthRub))
    dbSQL.commit()


@dp.message_handler(commands="start")
async def Start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text="Курс валют")
    keyboard.add(button)
    await message.answer("Привет", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Курс валют")
async def Weather_my_City(message: types.Message):
    sql.execute("SELECT * FROM course")
    answer = sql.fetchall()
    id = len(answer) - 1
    time = str(answer[id][0])
    UsdRub = answer[id][1]
    EurRub = answer[id][2]
    BtnUsd = answer[id][3]
    BtnRub = answer[id][4]
    EthUsd = answer[id][5]
    EthRub = answer[id][6]

    await message.answer("1 доллар равен " + UsdRub + " рубля\n1 евро равен " + EurRub + " рубля\n1 биткоин стоит " +
                         BtnRub + " рублей\n1 биткоин стоит "+ BtnUsd + " доларов\n1 эфириум стоит " + EthUsd +
                         " долларов\n1 эфириум стоит " + EthRub + " рублей\n\nСинхронизированно в " + time)


if __name__ == "__main__":
    DataRecording()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(DataRecording, 'interval', minutes=5)
    scheduler.start()
    logger.info("Start")
    executor.start_polling(dp, skip_updates=True)
