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

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

COMMAND_LIST = []


def escape_for_markdown(text: str) -> str:
    """
    Escapes text to use as plain text in a markdown document
    :param text: the original text
    :return: the escaped text
    """
    escaped = text.replace("*", "\\*").replace("_", "\\_")
    return escaped


def parse_telegram_command(text: str) -> (str, [str]):
    """
    Parses the given message to a command and its arguments
    :param text: the text to parse
    :return: the command and its argument list
    """
    if text is None or len(text) <= 0:
        return None, []

    if " " not in text:
        return text[1:], []
    else:
        command, rest = text.split(" ", 1)
        args = rest.split(" ")
        return command[1:], args


def generate_help_message(name: str, description: str, args: []) -> str:
    """
    Generates a command usage description
    :param name: name of the command
    :param description: command description
    :param args: command argument list
    :return:
    """

    argument_lines = list(map(lambda x: x.generate_argument_message(), args))
    arguments = "\n".join(argument_lines)

    argument_examples = " ".join(list(map(lambda x: x.example, args)))

    lines = [
        "/{}".format(escape_for_markdown(name)),
        description
    ]
    if len(arguments) > 0:
        lines.append("Arguments: ")
        lines.append(arguments)
        lines.append("Example:")
        lines.append("  `/{} {}`".format(name, argument_examples))

    return "\n".join(lines)


def generate_command_list() -> str:
    """
    :return: a Markdown styled text description of all available commands
    """
    return "\n\n".join([
        "Commands:",
        *COMMAND_LIST
    ])


def command(name: str, description: str = None, arguments: [] = None):
    """
    Decorator to turn a command handler function into a full fledged, shell like command
    """

    if arguments is None:
        arguments = []
    help_message = generate_help_message(name, description, arguments)

    global COMMAND_LIST
    COMMAND_LIST.append(help_message)

    def decorator(func: callable):
        if not callable(func):
            raise AttributeError("Unsupported type: {}".format(func))

        @functools.wraps(func)
        def wrapper(self, update: Update, context: CallbackContext, *args, **kwargs):
            bot = context.bot
            message = update.effective_message
            command, string_arguments = parse_telegram_command(message.text)
            chat_id = message.chat_id

            parsed_args = []
            try:
                if len(arguments) > len(args):
                    raise ValueError("Too many arguments!")

                for idx, arg in enumerate(arguments):
                    try:
                        string_arg = string_arguments[idx]
                    except IndexError:
                        string_arg = None
                    parsed = arg.parse_arg(string_arg)
                    parsed_args.append(parsed)
            except Exception as ex:
                LOGGER.error(ex)
                bot.send_message(chat_id=chat_id, text=str(ex),
                                 reply_to_message_id=message.message_id)

                bot.send_message(chat_id=chat_id, parse_mode=ParseMode.MARKDOWN,
                                 text=help_message,
                                 reply_to_message_id=message.message_id)
                return

            return func(self, update, context, *parsed_args, *args, **kwargs)

        return wrapper

    return decorator
