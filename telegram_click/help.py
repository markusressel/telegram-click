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
from telegram_click.util import escape_for_markdown


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
