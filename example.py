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

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, Updater, MessageHandler, CommandHandler, Filters

from telegram_click import generate_command_list
from telegram_click.argument import Argument, Flag
from telegram_click.decorator import command
from telegram_click.permission import GROUP_ADMIN, USER_ID, USER_NAME
from telegram_click.permission.base import Permission

logging.getLogger("telegram_click").setLevel(logging.DEBUG)


class MyPermission(Permission):
    def evaluate(self, update: Update, context: CallbackContext) -> bool:
        from_user = update.effective_message.from_user

        # do fancy stuff
        return True


class MyBot:
    name = None
    child_count = None

    def __init__(self):
        self._updater = Updater(
            token=os.environ.get("TELEGRAM_BOT_KEY"),
            use_context=True
        )

        handler_groups = {
            1: [
                CommandHandler(['help', 'h'],
                               filters=(~ Filters.forwarded) & (~ Filters.reply),
                               callback=self._commands_command_callback),
                CommandHandler('start',
                               filters=(~ Filters.forwarded) & (~ Filters.reply),
                               callback=self._start_command_callback),
                CommandHandler(['name', 'n'],
                               filters=(~ Filters.forwarded) & (~ Filters.reply),
                               callback=self._name_command_callback),
                CommandHandler(['age', 'a'],
                               filters=(~ Filters.forwarded) & (~ Filters.reply),
                               callback=self._age_command_callback),
                CommandHandler(['children', 'c'],
                               filters=(~ Filters.forwarded) & (~ Filters.reply),
                               callback=self._children_command_callback),
                # Unknown command handler
                MessageHandler(Filters.command, callback=self._unknown_command_callback)
            ]
        }

        for group, handlers in handler_groups.items():
            for handler in handlers:
                self._updater.dispatcher.add_handler(handler, group=group)

    def start(self):
        """
        Starts up the bot.
        This means filling the url pool and listening for messages.
        """
        self._updater.start_polling(clean=True)
        self._updater.idle()

    def _unknown_command_callback(self, update: Update, context: CallbackContext):
        self._send_command_list(update, context)

    # Optionally specify this command to list all available commands
    @command(name=['help', 'h'],
             description='List commands supported by this bot.')
    def _commands_command_callback(self, update: Update, context: CallbackContext):
        self._send_command_list(update, context)

    @command(name='start',
             description='Start bot interaction')
    def _start_command_callback(self, update: Update, context: CallbackContext):
        self._send_command_list(update, context)

    @staticmethod
    def _send_command_list(update: Update, context: CallbackContext):
        bot = context.bot
        chat_id = update.effective_message.chat_id
        text = generate_command_list(update, context)
        bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN)

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
                 )
             ])
    def _name_command_callback(self, update: Update, context: CallbackContext, name: str or None, flag: bool):
        chat_id = update.effective_chat.id
        if name is None:
            message = 'Current: {}'.format(self.name)
        else:
            self.name = name
            message = 'New: {}'.format(self.name)
        message += '\n' + 'Flag is: {}'.format(flag)
        context.bot.send_message(chat_id, message)

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
    def _age_command_callback(self, update: Update, context: CallbackContext, age: int):
        context.bot.send_message(update.effective_chat.id, 'New age: {}'.format(age))

    @command(name=['children', 'c'],
             description='Set children',
             arguments=[
                 Argument(name=['amount', 'a'],
                          description='The new amount',
                          type=float,
                          validator=lambda x: x >= 0,
                          example='1.57',
                          optional=True)
             ])
    def _children_command_callback(self, update: Update, context: CallbackContext, child_count: float or None):
        chat_id = update.effective_chat.id
        if child_count is None:
            context.bot.send_message(chat_id, 'Current: {}'.format(self.child_count))
        else:
            self.child_count = child_count
            context.bot.send_message(chat_id, 'New: {}'.format(child_count))


if __name__ == '__main__':
    my_bot = MyBot()
    my_bot.start()
