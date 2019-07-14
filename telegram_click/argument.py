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

from telegram_click import escape_for_markdown

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class Argument:

    def __init__(self, name: str, description: str, example: str, type: type = str, converter: callable = None,
                 default: any = None,
                 validator: callable = None):
        """
        Creates a command argument object
        :param name: the name of the command
        :param converter: an optional converter function to convert the string value to another type
        :param default: an optional default value
        :param validator: a validator function
        """
        self.name = name
        self.description = description
        self.example = example
        self.type = type
        if converter is None:
            if type is not str:
                raise ValueError("If you want to use a custom type you have to provide a converter function too!")
            self.converter = lambda x: x
        else:
            self.converter = converter
        self.default = default
        self.validator = validator

    def parse_arg(self, arg: str) -> any:
        """
        Tries to parse the given value
        :param arg: the string value
        :return: the parsed value
        """

        if self.default is not None and arg is None:
            return self.default

        parsed = self.converter(arg)
        if self.validator is not None:
            if not self.validator(parsed):
                raise ValueError("Invalid argument value: {}".format(arg))
        return parsed

    def generate_argument_message(self) -> str:
        """
        Generates the usage text for this argument
        :return: usage text line
        """
        message = "  {} (`{}`): {}".format(
            escape_for_markdown(self.name),
            self.type.__name__,
            escape_for_markdown(self.description)
        )
        if self.default is not None:
            message += " (default: {}".format(escape_for_markdown(self.default))
        return message


class Selection(Argument):
    """
    Convenience class for a command argument based on a predefined selection of allowed values
    """

    def __init__(self, name: str, description: str, allowed_values: [any], type: type = str, converter: callable = None,
                 default: any = None):
        self.allowed_values = allowed_values
        validator = lambda x: x in self.allowed_values
        super().__init__(name, description, allowed_values[0], type, converter, default, validator)

    def generate_argument_message(self):
        message = "  {} (`{}`): {}".format(
            escape_for_markdown(self.name),
            self.type.__name__,
            escape_for_markdown(self.description)
        )
        if self.default is not None:
            message += " (default: {}".format(escape_for_markdown(self.default))
        return message
