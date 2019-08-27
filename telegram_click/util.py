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
from collections import OrderedDict

from telegram import Bot

from telegram_click.const import ARG_NAMING_PREFIXES

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


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


def starts_with_naming_prefix(arg: str) -> bool:
    for prefix in ARG_NAMING_PREFIXES:
        if arg.startswith(prefix):
            return True

    return False


def remove_naming_prefix(arg: str) -> str:
    for prefix in ARG_NAMING_PREFIXES:
        if arg.startswith(prefix):
            return arg[len(prefix):]

    return arg


def split_named_args(str_args: [str]) -> ([(str, str)], [str]):
    """
    Separates named command arguments (including their values) from non-named arguments
    :return: list of (argument name, value) tuples, list of free-floating arguments
    """
    named = []
    non_named = []

    i = 0
    while i < len(str_args):
        arg = str_args[i]
        if starts_with_naming_prefix(arg):
            named_item = (remove_naming_prefix(arg), str_args[i + 1])
            named.append(named_item)
            i += 1
        else:
            non_named.append(arg)

        i += 1

    return named, non_named


def parse_command_args(arguments: str or None, expected_args: []) -> dict:
    """
    Parses the given argument text
    :param arguments: the argument text
    :param expected_args: a list of expected arguments
    :return: dictionary { argument-name -> value }
    """
    if arguments is None:
        arguments = ""

    import shlex
    str_args = shlex.split(arguments)
    named, floating = split_named_args(str_args)
    parsed_args = {}

    # map argument.name -> argument
    arg_name_map = OrderedDict()
    for expected_arg in expected_args:
        for name in expected_arg.names:
            arg_name_map[name] = expected_arg

    # process named args first
    for name, value in named:
        if name in arg_name_map:
            arg = arg_name_map[name]
            parsed_args[arg.name] = arg.parse_arg_value(value)
            for name in arg.names:
                arg_name_map.pop(name)
        else:
            raise ValueError("Unknown argument '{}'".format(name))

    # then floating args
    for floating_arg in floating:
        if len(arg_name_map) <= 0:
            # ignore excess arguments
            break

        arg = list(arg_name_map.values())[0]
        parsed_args[arg.name] = arg.parse_arg_value(floating_arg)
        for name in arg.names:
            arg_name_map.pop(name)

    # and then handle missing args
    while len(arg_name_map) > 0:
        name, arg = arg_name_map.popitem()
        parsed_args[arg.name] = arg.parse_arg_value(None)
        for name in list(filter(lambda x: x != name, arg.names)):
            arg_name_map.pop(name)

    return parsed_args


def split_command_from_args(text: str or None) -> (str or None, str or None):
    """
    Splits the command (including any target) from its arguments
    :param text: the full message
    :return: (command, args)
    """
    if text is None or len(text) <= 0:
        return None, None

    if " " in text:
        return text.split(" ", 1)
    else:
        return text, None


def split_command_from_target(bot_username: str, command: str or None) -> (str, str):
    """
    Determines the command target bot username
    :param bot_username: the username of this bot
    :param command: the command to check
    :return: (the command, the username of the targeted bot)
    """
    target = bot_username

    if command is None or len(command) <= 0:
        return command, target

    if '@' in command:
        command, target = command.split('@', 1)

    return command, target


def parse_telegram_command(bot_username: str, text: str, expected_args: []) -> (str, str, [str]):
    """
    Parses the given message to a command and its arguments
    :param bot_username: the username of the current bot
    :param text: the text to parse
    :param expected_args: expected arguments
    :return: the target bot username, command, and its argument list
    """
    command, args = split_command_from_args(text)
    command, target = split_command_from_target(bot_username, command)
    parsed_args = parse_command_args(args, expected_args)
    return command[1:], parsed_args


def generate_help_message(names: [str], description: str, args: []) -> str:
    """
    Generates a command usage description
    :param names: names of the command
    :param description: command description
    :param args: command argument list
    :return: help message
    """
    command_names = list(map(lambda x: "/{}".format(escape_for_markdown(x)), names))
    command_names_line = command_names[0]
    if len(command_names) > 1:
        command_names_line += " ({})".format(", ".join(command_names[1:]))

    argument_lines = list(map(lambda x: x.generate_argument_message(), args))
    arguments = "\n".join(argument_lines)

    argument_examples = " ".join(list(map(lambda x: x.example, args)))

    lines = [
        command_names_line,
        description
    ]
    if len(arguments) > 0:
        lines.extend([
            "Arguments: ",
            arguments,
            "Example:",
            "  `/{} {}`".format(names[0], argument_examples)
        ])

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
