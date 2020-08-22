#  Copyright (c) 2020 Markus Ressel
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

from telegram_click.const import *

LOGGER = logging.getLogger(__name__)


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
    str_args = shlex.split(arguments, posix=False)

    # map argument.name -> argument
    arg_name_map = OrderedDict()
    for expected_arg in expected_args:
        for name in expected_arg.names:
            arg_name_map[name] = expected_arg

    parsed_args = {}

    named_arg_idx = []
    for idx, arg_key in enumerate(str_args):
        if is_argument_key(arg_key):
            named_arg_idx.append(idx)

    # process named arguments first
    used_idx = list(named_arg_idx)
    for idx in named_arg_idx:
        arg_key = str_args[idx]
        arg_name = remove_naming_prefix(arg_key)
        value = None

        if ARG_VALUE_SEPARATOR_CHAR in arg_name:
            arg_name, value = arg_name.split(ARG_VALUE_SEPARATOR_CHAR, 1)

        if arg_name not in arg_name_map:
            raise ValueError("Unknown argument '{}'".format(arg_key))
        arg = arg_name_map[arg_name]

        if arg.flag:
            if value is not None:
                raise ValueError("Unexpected flag value: {}".format(arg_key))
            # if a flag is present, we assume the value "true"
            value = arg.parse_arg_value("True")
        else:
            if ARG_VALUE_SEPARATOR_CHAR not in arg_key:
                next_idx = idx + 1
                value = str_args[next_idx] if next_idx < len(str_args) else None
                used_idx.append(next_idx)

            if value is None:
                raise ValueError(
                    "Expected argument value for '{}' but found EOL".format(arg_key))
            if is_argument_key(value):
                raise ValueError(
                    "Expected argument value for '{}' but found named argument '{}'".format(arg_key, value))

        if is_quoted(value):
            value = value[1:-1]

        parsed_args[arg.name] = arg.parse_arg_value(value)
        for name in arg.names:
            arg_name_map.pop(name)

    # then process positional arguments
    remaining_idx = list(set(list(range(len(str_args)))) - set(used_idx))
    for idx in sorted(remaining_idx):
        if len(arg_name_map) <= 0:
            # ignore excess arguments
            break

        arg_key = str_args[idx]
        if is_quoted(arg_key):
            arg_key = arg_key[1:-1]
        arg = list(arg_name_map.values())[0]
        # ignore flags here, to prevent accidentally setting a flag value
        if arg.flag:
            continue
        parsed_args[arg.name] = arg.parse_arg_value(arg_key)
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
    command, _ = split_command_from_target(bot_username, command)
    parsed_args = parse_command_args(args, expected_args)
    return command[1:], parsed_args


def is_argument_key(text: str) -> bool:
    """
    Checks is a text has the form of an argument key
    :param text: the text to check
    :return: true if valid argument form, false otherwise
    """
    return (
            not is_quoted(text)
            and starts_with_naming_prefix(text)
    )


def is_quoted(text: str or any) -> bool:
    """
    Checks if the given text is quoted.
    Note: This method expects a stripped text!
          When passing something other than a str, the result will always be False.
    :param text: the text to check
    :return: True if quoted, false otherwise
    """
    if not isinstance(text, str):
        return False

    for char in QUOTE_CHARS:
        if text.startswith(char) and text.endswith(char):
            return True

    return False


def starts_with_naming_prefix(arg: str) -> bool:
    """
    Checks if the given string starts
    :param arg:
    :return:
    """
    for prefix in ARG_NAMING_PREFIXES:
        if arg.startswith(prefix):
            return True

    return False


def remove_naming_prefix(arg: str) -> str:
    """
    Removes the argument prefix from the given text
    :param arg: the original argument text
    :return: the argument name
    """
    for prefix in ARG_NAMING_PREFIXES:
        if arg.startswith(prefix):
            return arg[len(prefix):]

    return arg
