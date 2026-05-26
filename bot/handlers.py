"""Telegram update handlers."""
import requests
from bs4 import BeautifulSoup
import logging
import time
import json
from datetime import date
import certifi
# from selenium import webdriver
# from selenium.webdriver.common.by import By
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import html5lib
import gspread
import os
logger = logging.getLogger(__name__)

#Настройка парсинга сайта
# driver = webdriver.Chrome()
# driver.get('https://ibc.mirea.ru/')
s = requests.Session()
mirea_url = 'https://ibc.mirea.ru/books/search/?search_field='
s.headers.update({'Referer': mirea_url})
# csrf = form.find('input', {'name': 'csrfmiddlewaretoken'}).get('value')
#Настройка парсинга сайта


#Настройка подключения к API
CREDENTIALS_FILE = 'path/to/your/credentials.json'
WEB_APP_URL =os.getenv('WEB_APP_URL')
WEB_APP_URL2 =os.getenv('WEB_APP_URL2')
# ID вашей таблицы (можно найти в URL: https://docs.google.com/spreadsheets/d/ID_ТАБЛИЦЫ/edit)
SPREADSHEET_ID = '1tBoktUQPkdC4zwQdsyE3MGR5Kcf74MIl2M7rz2T4mEc'
RANGE_NAME = 'Class Data!A2:E' # "Название листа!диапазон"
#Настройка подключения к API



BOT_COMMANDS = (
    ("start", "Show the main menu"),
    ("update", "Обновление таблицы"),
)

MENU_HELP = "Help"
MENU_ABOUT = "About"
MENU_PING = "Ping"
global Glob_Message
# MAIN_MENU_KEYBOARD = ReplyKeyboardMarkup(
#     [[MENU_HELP, MENU_ABOUT], [MENU_PING]],
#     resize_keyboard=True,
#     is_persistent=True,
#     input_field_placeholder="Choose a menu item",
# )

HELP_TEXT = """Available commands:
/start - Start the bot
/help - Show help
/about - Show bot information
/ping - Check bot status

Send a normal text message and the bot will echo it back."""
USER_ID = [8293418325,5058627557,7751534678]

#Команды не относящиеся к сообщениям
def get_sheet_data(sheet_name=None):
    """Получить данные с конкретного листа"""
    url = WEB_APP_URL2

    if sheet_name:
        url += f'?sheet={sheet_name}'

    response = requests.get(url)
    return response.json() if response.status_code == 200 else None


def updat():
    day = str(date.today()).replace("-", ".")
    glob_date = []
    for i in range(len(k := (get_sheet_data("Лист1")['data'][2:]))):

        # Запросы к библиотеке миреа
        so = BeautifulSoup(s.get(mirea_url + k[i][2], timeout=10).text, 'html.parser')

        soup = so.find_all(class_="bib-desc")
        # Запросы к библиотеке миреа

        # for j in soup:
        #     print(j)
        # [x for x in soup if x.find_all("b")[1]]
        if len(soup) >= 1 and (k[i][17] == "") and soup[0].find_all(class_="year")[0].text == "Год издания:  2026":
            # if len(soup)>2:
            #     q = [x for x in soup if k[i][3][1:]==x.find_all("b")[1].text[3:]]
            #     if len(q)==1:
            #         soup=q
            # print(soup.find_all("b")[1])
            print(len(soup))
            print(soup[0].find_all(class_="year")[0].text)

            l = str(soup[0].find_all(target="_blank")[0])
            # получение данных книги
            book_share = l[l.find('"') + 1:l[l.find('"') + 1:].find('"') + l.find('"') + 1]
            request_book = BeautifulSoup(s.get("https://ibc.mirea.ru" + book_share, timeout=10).text, 'html.parser').find_all(
                class_="isbn")[0].text
            name = BeautifulSoup(s.get("https://ibc.mirea.ru" + book_share, timeout=10).text, 'html.parser').find_all(class_="author")[0].text
            # получение данных книги

            # Отправка данных в таблицу - дата публикации/выходные дан/isbn/ссылка

            Date = [day, name, request_book, "https://ibc.mirea.ru" + book_share]
            [requests.post(WEB_APP_URL, data=json.dumps({'range': "OPQR"[y] + str(i + 4), 'value': Date[y]})) for y in
             range(len(Date))]
            glob_date.append(Date)

    return glob_date
            # requests.post(WEB_APP_URL, data=json.dumps({'range': "O" + str(i + 4), 'value': request_book}))
            # requests.post(WEB_APP_URL, data=json.dumps({'range': "P" + str(i+4), 'value': soup[0].find_all("b")[1].text}))
            # requests.post(WEB_APP_URL, data=json.dumps({'range': "Q" + str(i + 4), 'value': request_book}))
            # requests.post(WEB_APP_URL, data=json.dumps({'range': "R" + str(i+4), 'value': book_share}))
            # Отправка данных в таблицу
#Команды не относящиеся к сообщениям

#Функции принятия команд/сообщений
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    message = update.effective_message
    user = update.effective_user
    if message is None:
        return
    ti = time.ctime(time.time())
    if user.id in USER_ID:
        await message.reply_text(
            f"Бот запущен 0.1")

        while 1:
            time.sleep(60)
            if ti[:-9]!=time.ctime(time.time())[:-9]:
                await message.reply_text(f"Плановое обновление "+str(time.ctime(time.time())))
                st = ""
                l = 0
                for i in updat():
                    strr = ""
                    [strr := strr + " " + j for j in i]
                    st += "\n" + strr
                    l += 1

                await message.reply_text("Таблица обновлена на " + str(l) + " строки\n" + st if l > 0 else "Таблица не обновлена")
                ti = time.ctime(time.time())

async def mes(update:Update)->None:
    message = update.effective_message
    await message.reply_text(f"Тест сообщения")




def pol(update:Update, context:ContextTypes.DEFAULT_TYPE):
    del context
    message = update.effective_message
    user = update.effective_user
    if user.id in USER_ID:
        while 1:
            message.reply_text(
            f"Бот запущен"
            )






async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    message = update.effective_message
    user = update.effective_user
    if user.id in USER_ID:
        print(message)
        # if message is None or not message.text:
        #     return
        # creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        # client = gspread.authorize(creds)
        # Данные для запроса

        # Отправляем форму
        # form = driver.find_element(By.CLASS_NAME, 'main__search-form')
        # input_field = form.find_element(By.TAG_NAME, 'input')
        # input_field.send_keys(message.text)
        # # Отправляем форму
        # form.submit()


        # response = s.post(form.get('action'), { 'search_field': message.text})
        # print(soup)
        st = ""
        l = 0
        for i in updat():
            strr = ""
            [strr:=strr+" "+j for j in i]
            st+="\n"+strr
            l+=1

        await message.reply_text("Таблица обновлена на "+str(l)+" строки\n"+st if l>0 else "Таблица не обновлена" )






    else:
        await message.reply_text(f"Айди не одобрен:\n{user.id}")


async def upd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    message = update.effective_message
    user = update.effective_user
    if user.id in [8293418325,5058627557,7751534678]:
        await message.reply_text(f"Обновление начато")
        st = ""
        l = 0
        for i in updat():
            s = ""
            [s := s + " " + j for j in i]
            st += "\n" + s
            l += 1



        await message.reply_text(
            "Таблица обновлена на " + str(l) + " строки\n" + st if l > 0 else "Таблица не обновлена")
    else:
        await message.reply_text(f"Айди не одобрен:\n{user.id}")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    message = update.effective_message
    if message is None:
        return

    await message.reply_text("Unknown command. Type /help for assistance.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Error while processing update: %s", update, exc_info=context.error)

    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Sorry, an error occurred while processing your message."
        )


async def set_bot_commands(application: Application) -> None:
    await application.bot.set_my_commands(BOT_COMMANDS)




def register_handlers(application: Application) -> None:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("update", upd))
    # application.add_handler(CommandHandler("pars", pars))
        # application.add_handler(CommandHandler("test", test))
    # application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    application.add_handler(
        MessageHandler(filters.TEXT, echo)
    )
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
