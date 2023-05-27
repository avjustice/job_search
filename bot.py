import logging
import random
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from config import API_TOKEN
from parser import make_params, get_moscow_time, get_info

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="I'm a bot, please talk to me!")


async def job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_from = (datetime.fromisoformat(get_moscow_time()) - timedelta(hours=24)).isoformat()
    params = make_params(text='Java', date_from=date_from, per_page=50)
    response = await get_info(request='https://api.hh.ru/vacancies', params=params)
    url = response.get('items')[0].get('alternate_url')
    await update.message.reply_text(url)


if __name__ == '__main__':
    application = ApplicationBuilder().token(API_TOKEN).build()

    start_handler = CommandHandler('start', start)
    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    job_handler = CommandHandler('job', job)

    application.add_handler(start_handler)
    # application.add_handler(echo_handler)
    application.add_handler(job_handler)

    application.run_polling()
