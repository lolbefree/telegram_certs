import os
import code128
import requests as requests
from telegram import Update
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
import logging
import pyodbc
from tabulate import tabulate
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import MessageHandler
from telegram.ext import Filters
# from config import token
import sql_querys
from PIL import Image, ImageDraw, ImageFont
import telegram
import not_for_git


button_help = "Розпочати"
check_balance = "Перевірити баланс сертифікату"
check_history = "Історія використання сертифікату"
get_cert_barcode = "Отримати"
get_back = "Повернутися"
show_certificate = "Отримати сертифікат"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
bot = telegram.Bot(token=not_for_git.token)


class BotSpares:
    def __init__(self):
        self.check_status = ""
        self.list_with_messages = list()
        self.server = not_for_git.db_server
        self.database = not_for_git.db_name
        self.username = not_for_git.db_user
        self.password = not_for_git.db_pw
        self.driver = '{ODBC Driver 17 for SQL Server}'  # Driver you need to connect to the database '{SQL Server}'  #
        self.numpad_mod = ""
        self.cnn = pyodbc.connect(
            'DRIVER=' + self.driver + ';PORT=port;SERVER=' + self.server + ';PORT=1443;DATABASE=' + self.database +
            ';UID=' + self.username +
            ';PWD=' + self.password)
        self.cursor = self.cnn.cursor()

    def button_help_handler(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            text=f"Розпочнемо", reply_markup=ReplyKeyboardRemove(),
        )
        text = update.message.text
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=get_cert_barcode, request_contact=True)
                ], [
                    KeyboardButton(text=get_back)
                ],
            ],
            resize_keyboard=True, )

        update.message.reply_text(
            text="Оберіть кнопку нижче", reply_markup=reply_markup,
        )


    def create_history_image(self, x):
        hight = 12.5
        img = Image.new('RGB', (275, int(hight * x.count("\n"))), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        font_size = 10
        unicode_font = ImageFont.truetype("consola.ttf", font_size)
        d.text((5, 0), x, font=unicode_font, fill=(0, 0, 0))

        img.save('pil_text_font.png')

    def add_keybord(self):

        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=show_certificate,)
                ],
                [
                    KeyboardButton(text=check_balance,)
                ],
                [
                    KeyboardButton(text=check_history)
                ],
            ],
            resize_keyboard=True, )
        return reply_markup

    def message_handler(self, update: Update, context: CallbackContext):
        text = update.message.text
        if text == check_balance:
            self.check_status = check_balance
            return self.button_help_handler(update, context)
        if text == check_history:
            self.check_status = check_history
            return self.button_help_handler(update, context)
        if text == show_certificate:
            self.check_status = show_certificate
            return self.button_help_handler(update, context)

        else:
            update.message.reply_text(

                text="Оберіть кнопку нижче", reply_markup=self.add_keybord(),
            )

    def get_chat_id(self, update, context):
        chat_id = -1
        if update.message is not None:
            # text message
            chat_id = update.message.chat.id
        elif update.callback_query is not None:
            # callback message
            chat_id = update.callback_query.message.chat.id
        elif update.poll is not None:
            # answer in Poll
            chat_id = context.bot_data[update.poll.id]

        return chat_id

    def crate_cert_picture(self, cert_number, update: Update, context: CallbackContext):
        cd = code128.image('{}'.format(cert_number))
        cd.save("{}//{}.png".format(os.getcwd(), cert_number))
        img1 = Image.open(f'{os.getcwd()}//cert.jpg')  # main image
        new_barcode = Image.open("{}//{}.png".format(os.getcwd(), cert_number))

        img1.paste(new_barcode, (50, 950))  # paste barcode to main image
        img1.save(f"{os.getcwd()}//img_with_barcode.png")
        chat_id = self.get_chat_id(update, context)
        bot.send_photo(chat_id, open("img_with_barcode.png", 'rb'), reply_markup=self.add_keybord())
        os.remove(f"{os.getcwd()}//img_with_barcode.png")
        os.remove(f"{os.getcwd()}//{cert_number}.png")

    def contact_callback(self, update, context):
        contact = update.effective_message.contact
        self.phone = contact.phone_number[3:]
        print(f"0{self.phone} get {self.check_status}")
        if len(list(self.cursor.execute(sql_querys.balance(self.phone)))) == 0:
            message1 = f"Cертифікату за номером 0{self.phone} -  не знайдено"
            update.message.reply_text(
                text=message1,
                reply_markup=self.add_keybord(), )
        elif show_certificate == self.check_status:
            res = list(self.cursor.execute(sql_querys.balance(self.phone)))
            self.crate_cert_picture(res[0][0], update, context)
        elif check_balance == self.check_status:
            res = list(self.cursor.execute(sql_querys.balance(self.phone)))
            # print(sql_querys.balance(self.phone))
            # print(res)
            message1 = f"Шановний(а) {res[0][1]}, залишок по сертифікату {res[0][0]} - {res[0][2]} грн."
            update.message.reply_text(
                text=message1,
                reply_markup=self.add_keybord(), )
            self.check_status = ""

        elif check_history == self.check_status:
            # print(sql_querys.history(self.phone))
            res = list(self.cursor.execute(sql_querys.history(self.phone)))
            # print(res)
            if len(res[0]) == 1:
                message1 = f"Історії по сертифікату  {res[0][0]} -  не знайдено"
                update.message.reply_text(
                    text=message1,
                    reply_markup=self.add_keybord(), )
            else:
                res = list(self.cursor.execute(sql_querys.history(self.phone)))

                table = (tabulate(res, headers=["НЗ", "Дата", "Сума", "Залишок"], tablefmt="grid"))
                # print(table)
                self.create_history_image(table)
                chat_id = self.get_chat_id(update, context)
                # print(chat_id)
                bot.send_photo(chat_id, open("pil_text_font.png", 'rb'), reply_markup=self.add_keybord())
                os.remove("pil_text_font.png")


            self.check_status = ""



    def error(self, update, context):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(use_context=True,
                      token=not_for_git.token)
    m = BotSpares()
    updater.dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=m.message_handler))
    updater.dispatcher.add_error_handler(MessageHandler(filters=Filters.all, callback=m.error))
    updater.dispatcher.add_handler(MessageHandler(filters=Filters.contact, callback=m.contact_callback))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
