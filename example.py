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

from telegram_click import generate_command_list, CommandTarget
from telegram_click.argument import Argument
from telegram_click.decorator import command
from telegram_click.permission import GROUP_ADMIN, USER_ID, NOBODY
from telegram_click.permission.base import Permission

logging.basicConfig(level=logging.DEBUG)


class MyPermission(Permission):
    def evaluate(self, update: Update, context: CallbackContext) -> bool:
        from_user = update.effective_message.from_user

        # do fancy stuff
        return True


class MyBot:

    def __init__(self):
        self._updater = Updater(token=os.environ.get("TELEGRAM_BOT_KEY"),
                                use_context=True)

        handler_groups = {
            1: [MessageHandler(Filters.text, callback=self._message_callback),
                CommandHandler('commands',
                               filters=(~ Filters.forwarded) & (~ Filters.reply),
                               callback=self._commands_command_callback),
                CommandHandler('start',
                               filters=(~ Filters.forwarded) & (~ Filters.reply),
                               callback=self._start_command_callback),
                CommandHandler('name',
                               filters=(~ Filters.forwarded) & (~ Filters.reply),
                               callback=self._name_command_callback),
                CommandHandler('age',
                               filters=(~ Filters.forwarded) & (~ Filters.reply),
                               callback=self._age_command_callback),
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

    def _message_callback(self, update: Update, context: CallbackContext):
        text = update.effective_message.text
        print("Message: {}".format(text))
        pass

    # optionally specify this callback to send a list of all available commands if
    # an unsupported command is used
    @command(name="commands",
             description="List commands supported by this bot.",
             permissions=NOBODY,
             command_target=CommandTarget.UNSPECIFIED | CommandTarget.SELF)
    def _unknown_command_callback(self, update: Update, context: CallbackContext):
        bot = context.bot
        chat_id = update.effective_message.chat_id
        text = generate_command_list(update, context)
        bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN)

    # Optionally specify this command to list all available commands
    @command(name="commands",
             description="List commands supported by this bot.")
    def _commands_command_callback(self, update: Update, context: CallbackContext):
        self._unknown_command_callback(update, context)

    @command(name='start',
             description='Start bot interaction')
    def _start_command_callback(self, update: Update, context: CallbackContext):
        # do something
        pass

    @command(name='name',
             description='Set a name',
             arguments=[
                 Argument(name='name',
                          description='The new name',
                          validator=lambda x: x.strip(),
                          example='Markus')
             ])
    def _name_command_callback(self, update: Update, context: CallbackContext, name: str):
        context.bot.send_message(update.effective_chat.id, "New name: {}".format(name))

    @command(name='age',
             description='Set age',
             arguments=[
                 Argument(name='age',
                          description='The new age',
                          type=int,
                          validator=lambda x: x > 0,
                          example='25')
             ],
             permissions=MyPermission() & ~ GROUP_ADMIN & (USER_ID(123456)))
    def _age_command_callback(self, update: Update, context: CallbackContext, age: int):
        context.bot.send_message(update.effective_chat.id, "New age: {}".format(age))


if __name__ == '__main__':
    my_bot = MyBot()
    my_bot.start()
