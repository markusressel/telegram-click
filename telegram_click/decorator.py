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
import functools
import logging

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from telegram_click.argument import Argument
from telegram_click.util import generate_help_message, parse_telegram_command, send_message

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def command(name: str, description: str = None,
            arguments: [Argument] = None,
            permissions: [] = None,
            print_error: bool = True):
    """
    Decorator to turn a command handler function into a full fledged, shell like command
    :param name: Name of the command
    :param description: a short description of the command
    :param arguments: list of command argument description objects
    :param permissions: list of required permissions to run this command
    :param print_error: sends the exception message to the chat of origin if set to True, False sends a general error message
    """

    if arguments is None:
        arguments = []
    if permissions is None:
        permissions = []

    help_message = generate_help_message(name, description, arguments)

    from telegram_click import COMMAND_LIST
    COMMAND_LIST.append(help_message)

    def decorator(func: callable):
        if not callable(func):
            raise AttributeError("Unsupported type: {}".format(func))

        @functools.wraps(func)
        def wrapper(self, update: Update, context: CallbackContext, *args, **kwargs):
            bot = context.bot
            message = update.effective_message
            chat_id = message.chat_id

            command, string_arguments = parse_telegram_command(message.text)

            parsed_args = []
            try:
                for permission in permissions:
                    if not permission.evaluate(update, context, command):
                        raise PermissionError("You do not have permission to use this command")

                if len(string_arguments) > len(arguments):
                    raise ValueError("Too many arguments!")

                for idx, arg in enumerate(arguments):
                    try:
                        string_arg = string_arguments[idx]
                    except IndexError:
                        string_arg = None
                    parsed = arg.parse_arg(string_arg)
                    parsed_args.append(parsed)
            except PermissionError as ex:
                send_message(bot, chat_id=chat_id, message=":no_entry_sign: `{}`".format(str(ex)),
                             parse_mode=ParseMode.MARKDOWN,
                             reply_to=message.message_id)
                return
            except Exception as ex:
                LOGGER.error(ex)
                text = "\n".join([
                    ":exclamation: `{}`".format(str(ex)),
                    "",
                    help_message
                ])
                send_message(bot, chat_id=chat_id, message=text, parse_mode=ParseMode.MARKDOWN,
                             reply_to=message.message_id)
                return

            try:
                return func(self, update, context, *parsed_args, *args, **kwargs)
            except Exception as ex:
                LOGGER.error(ex)
                if print_error:
                    text = ":boom: `{}`".format(str(ex))
                else:
                    text = "There was an error executing your command :worried:"
                send_message(bot, chat_id=chat_id, message=text, parse_mode=ParseMode.MARKDOWN,
                             reply_to=message.message_id)

        return wrapper

    return decorator
