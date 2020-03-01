#  Copyright (c) 2019 Markus Ressel
#  .
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  .
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#  .
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


def find_duplicates(l: list) -> []:
    """
    Finds duplicate entries in the given list
    :param l: the list to check
    :return: map of (value -> list of indexes)
    """
    if not len(l) != len(set(l)):
        return []

    # remember indexes of items with equal hash
    tmp = {}
    for i, v in enumerate(l):
        if v in tmp.keys():
            tmp[v].append(i)
        else:
            tmp[v] = [i]

    result = {}
    for k, v in tmp.items():
        if len(v) > 1:
            result[k] = v

    return result


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


def escape_for_markdown(text: str or None) -> str:
    """
    Escapes text to use as plain text in a markdown document
    :param text: the original text
    :return: the escaped text
    """
    text = str(text)
    escaped = text.replace("*", "\\*").replace("_", "\\_")
    return escaped


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
