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
from typing import List

from telegram_click.argument import Argument
from telegram_click.const import ARG_NAMING_PREFIXES
from telegram_click.util import escape_for_markdown


def generate_help_message(names: [str], description: str, args: List[Argument]) -> str:
    """
    Generates a command usage description
    :param names: names of the command
    :param description: command description
    :param args: command argument list
    :return: help message
    """
    synopsis = generate_synopsis(names, args)
    args_description = generate_argument_description(args)
    argument_examples = " ".join(list(map(lambda x: x.example, args)))

    lines = [
        synopsis,
        description
    ]
    if len(args) > 0:
        lines.extend([
            "Arguments: ",
            args_description,
            "Example:",
            "  `/{} {}`".format(names[0], argument_examples)
        ])

    return "\n".join(lines)


def generate_synopsis(names: [str], args: List[Argument]):
    """
    Generates the synopsis for a command
    :param names: command names
    :param args: arguments
    :return:
    """
    command_names = list(map(lambda x: "/{}".format(escape_for_markdown(x)), names))
    synopsis = command_names[0]
    if len(args) > 0 and any(map(lambda x: not x.optional, args)):
        synopsis += " [[OPTIONS]]"
    if len(command_names) > 1:
        synopsis += " ({})".format(", ".join(command_names[1:]))

    return synopsis


def generate_argument_description(args):
    """
    Generates the description of all given arguments
    :param args: arguments
    :return: description
    """
    sorted_args = sorted(args, key=lambda x: (not x.flag, x.optional, x.name))
    argument_lines = list(map(generate_argument_message, sorted_args))
    return "\n".join(argument_lines)


def generate_argument_message(arg: Argument) -> str:
    """
    Generates the usage text for an argument
    :param arg: the argument
    :return: usage text line
    """
    arg_prefix = next(iter(ARG_NAMING_PREFIXES))
    arg_names = list(map(lambda x: "`{}{}`".format(arg_prefix, x), arg.names))

    message = "  " + ", ".join(arg_names)
    if not arg.flag:
        message += "\t\t`{}`".format(arg.type.__name__.upper())
    message += "\t\t" + escape_for_markdown(arg.description)

    if arg.optional and not arg.flag:
        message += "\t(`{}`)".format(escape_for_markdown(arg.default))
    return message
