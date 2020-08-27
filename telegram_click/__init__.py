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

from telegram import Update
from telegram.ext import CallbackContext

from telegram_click.const import *

LOGGER = logging.getLogger(__name__)

# global list of all commands
COMMAND_LIST = []


class CommandTarget:
    """
    Values used to specify what command target (/command@target) to accept
    """
    # no target is specified (meaning there is no "@" in command)
    UNSPECIFIED = 1 << 0
    # directly targeted at this bot
    SELF = 1 << 1
    # directly targeted at another bot
    OTHER = 1 << 2
    # any of them
    ANY = UNSPECIFIED | SELF | OTHER


def generate_command_list(update: Update, context: CallbackContext) -> str:
    """
    :return: a Markdown styled text description of all available commands
    """
    commands_with_permission = list(
        filter(lambda x: x[KEY_PERMISSIONS] is None or x[KEY_PERMISSIONS].evaluate(update, context), COMMAND_LIST))
    commands_not_hidden = list(
        filter(lambda x: not x[KEY_HIDDEN] if isinstance(x[KEY_HIDDEN], bool)
        else not x[KEY_HIDDEN](update, context) if callable(x[KEY_HIDDEN])
        else True, commands_with_permission))
    sorted_commands = sorted(commands_not_hidden, key=lambda x: (x[KEY_NAMES][0].lower(), len(x[KEY_ARGUMENTS])))
    help_messages = list(map(lambda x: x[KEY_HELP_MESSAGE], sorted_commands))

    if len(COMMAND_LIST) <= 0:
        return "This bot does not have any commands."

    if len(commands_not_hidden) <= 0:
        return "You do not have permission to use commands."

    return "\n\n".join([
        *help_messages
    ])
