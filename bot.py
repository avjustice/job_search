import logging
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, \
    PicklePersistence
from config import API_TOKEN
from parser import make_params, get_moscow_time, get_info

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['last_time'] = (datetime.fromisoformat(get_moscow_time()) - timedelta(hours=24)).isoformat()
    await update.message.reply_text(
        text=f"Здравствуйте, {update.effective_user.first_name}.\n"
             f"Это бот по поиску вакансий на hh.ru.\n"
             f"Напишите вакансию, которую ищете"

    )
    return 1


async def set_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_aim = update.message.text
    context.user_data['text'] = user_aim
    await update.message.reply_text(
        text="Сохранил изменения.\n"
             "Используйте /job для поиска вакансий")
    return 2


async def job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_from, text = await get_date_from_and_text(context)
    params = make_params(text=text, date_from=date_from, per_page=50)
    response = await get_info(request='https://api.hh.ru/vacancies', params=params)
    context.user_data['last_time'] = get_moscow_time()
    number_of_vacancies = min(response.get('per_page'), response.get('found'))
    urls = [f"{response.get('items')[i].get('alternate_url')} {response.get('items')[i].get('name')}"
            for i in range(number_of_vacancies)]
    if urls:
        await update.message.reply_text('\n\n'.join(urls), disable_web_page_preview=True)
    else:
        await update.message.reply_text('Пока нет новых вакансий')
    return 2


async def get_date_from_and_text(context):
    date_from = context.user_data.get('last_time')
    if not date_from:
        date_from = (datetime.fromisoformat(get_moscow_time()) - timedelta(hours=24)).isoformat()
    text = context.user_data.get('text') or ''
    return date_from, text


if __name__ == '__main__':
    persistence = PicklePersistence(filepath="hh_vacancies")
    application = ApplicationBuilder().token(API_TOKEN).persistence(persistence).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
        ],
        states={
            1: [MessageHandler(filters.TEXT, set_text)],
            2: [CommandHandler("job", job)],
        },
        fallbacks=[CommandHandler("start", start),
                   CommandHandler("job", job),
                   CommandHandler("set_text", set_text)],
        persistent=True,
        name='conversation'
    )
    application.add_handler(conv_handler)

    # start_handler = CommandHandler('start', start)
    # # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    # set_handler = CommandHandler('set_text', set_text)
    # job_handler = CommandHandler('job', job)
    #
    # application.add_handler(start_handler)
    # application.add_handler(set_handler)
    # # application.add_handler(echo_handler)
    # application.add_handler(job_handler)

    application.run_polling()
