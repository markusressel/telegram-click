#  Copyright (c) 2019 Markus Ressel
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
import logging
import os

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CommandHandler, filters, ApplicationBuilder

from telegram_click import generate_command_list
from telegram_click.argument import Argument, Flag
from telegram_click.decorator import command
from telegram_click.error_handler import ErrorHandler
from telegram_click.permission import GROUP_ADMIN, USER_ID, USER_NAME, NOBODY
from telegram_click.permission.base import Permission

logging.getLogger("telegram_click").setLevel(logging.DEBUG)


class MyPermission(Permission):
    async def evaluate(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        from_user = update.effective_message.from_user

        # do fancy stuff
        return True


class MyErrorHandler(ErrorHandler):
    """
    Example of a custom error handler
    """

    async def on_permission_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  permissions: Permission) -> bool:
        bot = context.bot
        message = update.effective_message
        chat_id = message.chat_id

        text = "YOU SHALL NOT PASS! :hand::mage:"

        from telegram_click.util import send_message
        await send_message(bot, chat_id=chat_id,
                           message=text,
                           reply_to=message.message_id)

        return True

    async def on_validation_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE, exception: Exception,
                                  help_message: str) -> bool:
        # return False to let the `DefaultErrorHandler` process this
        return False

    async def on_execution_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                 exception: Exception) -> bool:
        # do nothing when an execution error occurs
        return True


def hide_whois_if_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    return user_id not in [123456]


class MyBot:
    name = None
    child_count = None

    def __init__(self):
        telegram_bot_token = os.environ.get("TELEGRAM_BOT_KEY")
        self._app = ApplicationBuilder().token(telegram_bot_token).build()

        handler_groups = {
            1: [
                CommandHandler(['help', 'h'],
                               filters=(~ filters.FORWARDED) & (~ filters.REPLY),
                               callback=self._commands_command_callback),
                CommandHandler('start',
                               filters=(~ filters.FORWARDED) & (~ filters.REPLY),
                               callback=self._start_command_callback),
                CommandHandler('whois',
                               filters=(~ filters.FORWARDED) & (~ filters.REPLY),
                               callback=self._whois_command_callback),
                CommandHandler(['name', 'n'],
                               filters=(~ filters.FORWARDED) & (~ filters.REPLY),
                               callback=self._name_command_callback),
                CommandHandler(['age', 'a'],
                               filters=(~ filters.FORWARDED) & (~ filters.REPLY),
                               callback=self._age_command_callback),
                CommandHandler(['children', 'c'],
                               filters=(~ filters.FORWARDED) & (~ filters.REPLY),
                               callback=self._children_command_callback),
                # Unknown command handler
                MessageHandler(filters.COMMAND, callback=self._unknown_command_callback)
            ]
        }

        for group, handlers in handler_groups.items():
            for handler in handlers:
                self._app.add_handler(handler, group=group)

    def start(self):
        """
        Starts up the bot.
        This means filling the url pool and listening for messages.
        """
        self._app.run_polling()

    async def _unknown_command_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._send_command_list(update, context)

    # Optionally specify this command to list all available commands
    @command(name=['help', 'h'],
             description='List commands supported by this bot.')
    async def _commands_command_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._send_command_list(update, context)

    @command(name='start',
             description='Start bot interaction')
    async def _start_command_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._send_command_list(update, context)

    @command(name='whois',
             description='Some easter-egg',
             hidden=hide_whois_if_admin)
    async def _whois_command_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        bot = context.bot
        chat_id = update.effective_message.chat_id
        text = update.effective_user.id
        await bot.send_message(chat_id, text, parse_mode="MARKDOWN")

    @staticmethod
    async def _send_command_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
        bot = context.bot
        chat_id = update.effective_message.chat_id
        text = await generate_command_list(update, context)
        await bot.send_message(chat_id, text, parse_mode="MARKDOWN")

    @command(name=['name', 'n'],
             description='Get/Set a name',
             arguments=[
                 Argument(name=['name', 'n'],
                          description='The new name',
                          validator=lambda x: x.strip(),
                          optional=True,
                          example='Markus'),
                 Flag(
                     name=['flag', 'f'],
                     description="Some flag that changes the command behaviour."
                 ),
                 Flag(
                     name=['flag2', 'F'],
                     description="Some other flag."
                 )
             ])
    async def _name_command_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, name: str or None,
                                     flag: bool,
                                     flag2: bool):
        chat_id = update.effective_chat.id
        if name is None:
            message = 'Current: {}'.format(self.name)
        else:
            self.name = name
            message = 'New: {}'.format(self.name)
        message += '\n' + 'Flag is: {}'.format(flag)
        message += '\n' + 'Flag2 is: {}'.format(flag2)
        await context.bot.send_message(chat_id, message)

    @command(name=['age', 'a'],
             description='Set age',
             arguments=[
                 Argument(name=['age', 'a'],
                          description='The new age',
                          type=int,
                          validator=lambda x: x > 0,
                          example='25')
             ],
             permissions=MyPermission() & ~ GROUP_ADMIN & (USER_NAME('markusressel') | USER_ID(123456)))
    async def _age_command_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, age: int):
        await context.bot.send_message(update.effective_chat.id, 'New age: {}'.format(age))

    @command(name=['children', 'c'],
             description='Set children amount',
             arguments=[
                 Argument(name=['amount', 'a'],
                          description='The new amount',
                          type=float,
                          validator=lambda x: x >= 0,
                          example='1.57')
             ],
             permissions=NOBODY,
             error_handler=MyErrorHandler())
    async def _children_command_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                         amount: float or None):
        chat_id = update.effective_chat.id
        if amount is None:
            await context.bot.send_message(chat_id, 'Current: {}'.format(self.child_count))
        else:
            self.child_count = amount
            await context.bot.send_message(chat_id, 'New: {}'.format(amount))


if __name__ == '__main__':
    my_bot = MyBot()
    my_bot.start()
