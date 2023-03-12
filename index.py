import os
from io import BytesIO
from queue import Queue
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Dispatcher
from movies_scraper import search_movies, get_movie


TOKEN = os.getenv("TOKEN")
URL = "https://sb-azure.vercel.app"
bot = Bot(TOKEN)


def welcome(update, context) -> None:
    update.message.reply_text(f"𝐇𝐞𝐥𝐥𝐨 {update.message.from_user.first_name},𝐖ᴇʟᴄᴏᴍᴇ 𝐓ᴏ Eᴍᴘɪʀᴇ Mᴏᴠɪᴇs Rᴇǫᴜᴇsᴛ Bᴏᴛ.\n\n"
                              f"➪ 𝐈 𝐀ᴍ 𝐒ɪᴍᴘʟᴇ 𝐌ᴏᴠɪᴇs 𝐏ʀᴏᴠɪᴅᴇʀ 𝐁ᴏᴛ\n"
                              f"➪ 𝐉ᴏɪɴ 𝐌ᴏᴠɪᴇs 𝐑ᴇǫᴜᴇsᴛ 𝐆ʀᴏᴜᴘ 𝐅ᴏʀ 𝐒ᴜᴘᴘᴏʀᴛ\n"
                              f"✪ 𝐃ᴇᴠᴇʟᴏᴘᴇʀ @EmpireOwnerobot\n"
                              f"➪ 𝗔𝗱𝗱 𝗦𝗼𝗺𝗲 𝗠𝗲𝗺𝗯𝗲𝗿𝘀 𝗜𝗻 𝗥𝗲𝗤𝘂𝗲𝘀𝘁 𝗚𝗿𝗼𝘂𝗽 𝗢𝗹𝗱 𝗚𝗿𝗼𝘂𝗽 𝗕𝗮𝗻𝗻𝗲𝗱\n\n"
                              f"✪ 𝐆ʀᴏᴜᴘ @MovieEmpire01\n"
                              f"➪ 𝗥𝗲𝗤𝘂𝗲𝘀𝘁 𝗬𝗼𝘂𝗿 𝗙𝗮𝘃𝗼𝘂𝗿𝗶𝘁𝗲 𝗠𝗼𝘃𝗶𝗲𝘀\n")


def find_movie(update, context):
    search_results = update.message.reply_text("Processing...")
    query = update.message.text
    movies_list = search_movies(query)
    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = InlineKeyboardButton(movie["title"], callback_data=movie["id"])
            keyboards.append([keyboard])
        reply_markup = InlineKeyboardMarkup(keyboards)
        search_results.edit_text('Search Results...', reply_markup=reply_markup)
    else:
        search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')


def movie_result(update, context) -> None:
    query = update.callback_query
    s = get_movie(query.data)
    response = requests.get(s["img"])
    img = BytesIO(response.content)
    query.message.reply_photo(photo=img, caption=f"🎥 {s['title']}")
    link = ""
    links = s["links"]
    for i in links:
        link += "🎬" + i + "\n" + links[i] + "\n\n"
    caption = f"⚡ Fast Download Links :-\n\n{link}"
    if len(caption) > 4095:
        for x in range(0, len(caption), 4095):
            query.message.reply_text(text=caption[x:x+4095])
    else:
        query.message.reply_text(text=caption)


def setup():
    update_queue = Queue()
    dispatcher = Dispatcher(bot, update_queue, use_context=True)
    dispatcher.add_handler(CommandHandler('start', welcome))
    dispatcher.add_handler(MessageHandler(Filters.text, find_movie))
    dispatcher.add_handler(CallbackQueryHandler(movie_result))
    return dispatcher


app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/{}'.format(TOKEN), methods=['GET', 'POST'])
def respond():
    update = Update.de_json(request.get_json(force=True), bot)
    setup().process_update(update)
    return 'ok'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}/{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"
