import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters
from datetime import date

from scraper import get_menu, restaurant_codes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


from keys import keys


tmp = [
    [i.capitalize() for i in restaurant_codes.keys()],
    ['Cancel']
]
markup = ReplyKeyboardMarkup(
    tmp,
    one_time_keyboard=True,
)


def make_pretty(menu):
    pretty = ""
    for option in menu:
        pretty += f"<u><b>{option['name']}</b></u> {option['description']} - (<i>{option['price']}k</i>r)\n<i>{' '.join(('[' + tag + ']' for tag in option['tags']))}</i>\n\n"
        
    return pretty


async def start(update, context):
    ''' Send a message when the /start command is issued. '''
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Ask me what's for lunch today... Go on... I dare you!",
    )
    
async def help(update, context):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        f'/start -> Welcome message\n/menu -> Show a menu, available restaurants are: {", ".join([i.capitalize() for i in restaurant_codes.keys()])}\n/help -> Show this message\n/credits -> Acknowledge the developers\n\n'
    )
    
async def credits(update, context):
    await update.message.reply_text(
        'This bot was developed single-handedly by Frank Fourlas and no on else in the entire universe... Especially not Marios Stamatopoulos...'
    )
    
async def menu(update, context):
    await update.message.reply_text(
        "Which restaurant's menu would you like to see? "
        "You can choose from the following restaurants:",
        reply_markup=markup,
    )
    
    return 0

async def restaurant(update, context):
    code = update.message.text.lower()
    menu = get_menu(code)
    
    if menu is None:
        await update.message.reply_text(
            "Sorry, I couldn't find that restaurant. Try again?",
            reply_markup=markup,
        )
        return 0
    
    await update.message.reply_html(
        f"Here's the menu for <b>{code.capitalize()}</b> for today, {date.today().strftime('%A, %d  %B %Y')}:\n\n{make_pretty(menu)}",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

async def cancel(update, context):
    await update.message.reply_text(
        "Keep the change, you hungry animal!",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


if __name__ == '__main__':
    app = Application.builder().token(keys['telegram']).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('credits', credits))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('menu', menu)],
        states = {
            0: [
                MessageHandler(
                    filters.Regex(f"^({'|'.join([i.capitalize() for i in restaurant_codes.keys()])})$"),
                    restaurant
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Cancel$"), cancel)],
    ))

    app.run_polling()
