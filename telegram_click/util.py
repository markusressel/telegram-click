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

from telegram import Bot

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def find_first(args: [], type: type):
    """
    Finds the first element in the list of the given type
    :param args: list of elements
    :param type: expected type
    :return: item or None
    """
    for arg in args:
        if isinstance(arg, type):
            return arg


def escape_for_markdown(text: str) -> str:
    """
    Escapes text to use as plain text in a markdown document
    :param text: the original text
    :return: the escaped text
    """
    escaped = text.replace("*", "\\*").replace("_", "\\_")
    return escaped


def parse_telegram_command(bot_username: str, text: str) -> (str, str, [str]):
    """
    Parses the given message to a command and its arguments
    :param bot_username: the username of the current bot
    :param text: the text to parse
    :return: the target bot username, command, and its argument list
    """
    import shlex

    target = bot_username

    if text is None or len(text) <= 0:
        return target, None, []

    if " " in text:
        first, rest = text.split(" ", 1)
    else:
        first = text
        rest = ""

    if '@' in first:
        command, target = first.split('@', 1)
        command = command
        target = target
    else:
        command = first

    args = shlex.split(rest)
    return target, command[1:], args


def generate_help_message(name: str, description: str, args: []) -> str:
    """
    Generates a command usage description
    :param name: name of the command
    :param description: command description
    :param args: command argument list
    :return: help message
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


def send_message(bot: Bot, chat_id: str, message: str, parse_mode: str = None, reply_to: int = None):
    """
    Sends a text message to the given chat
    :param bot: the bot
    :param chat_id: the chat id to send the message to
    :param message: the message to chat (may contain emoji aliases)
    :param parse_mode: specify whether to parse the text as markdown or HTML
    :param reply_to: the message id to reply to
    """
    from emoji import emojize

    emojized_text = emojize(message, use_aliases=True)
    bot.send_message(chat_id=chat_id, parse_mode=parse_mode, text=emojized_text, reply_to_message_id=reply_to)
