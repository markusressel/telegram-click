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

from telegram_click.util import escape_for_markdown

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class Argument:
    """
    Command argument description
    """

    def __init__(self, name: str, description: str, example: str, type: type = str, converter: callable = None,
                 default: any = None, validator: callable = None):
        """
        Creates a command argument object
        :param name: the name of the argument
        :param description: a short description of the argument
        :param example: an example (string!) value for this argument
        :param type: the expected type of the argument
        :param converter: a converter function to convert the string value to the expected type
        :param default: an optional default value
        :param validator: a validator function
        """
        self.name = name
        self.description = description
        self.example = example
        self.type = type
        if converter is None:
            if type is str:
                self.converter = lambda x: x
            elif type is bool:
                self.converter = self._boolean_converter
            elif type is int:
                self.converter = lambda x: int(x)
            elif type is float:
                self.converter = lambda x: float(x)
            else:
                raise ValueError("If you want to use a custom type you have to provide a converter function too!")
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

    @staticmethod
    def _boolean_converter(value: str) -> bool:
        """
        Converts a string to a boolean
        :param value: string value
        :return: boolean
        """
        s = str(value).lower()
        if s in ['y', 'yes', 'true', 't', '1']:
            return True
        elif s in ['n', 'no', 'false', 'f', '0']:
            return False
        else:
            raise ValueError("Invalid value '{}'".format(value))


class Selection(Argument):
    """
    Convenience class for a command argument based on a predefined selection of allowed values
    """

    def __init__(self, name: str, description: str, allowed_values: [any], type: type = str, converter: callable = None,
                 default: any = None):
        """

        :param name: the name of the argument
        :param description: a short description of the argument
        :param allowed_values: list of allowed (target type) values
        :param type: the expected type of the argument
        :param converter: a converter function to convert the string value to the expected type
        :param default: an optional default value
        """
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
