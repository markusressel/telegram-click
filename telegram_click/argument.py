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

from telegram_click.const import ARG_VALUE_SEPARATOR_CHAR
from telegram_click.util import find_duplicates

LOGGER = logging.getLogger(__name__)


class Argument:
    """
    Command argument description
    """

    def __init__(self, name: str or [str], description: str, example: str, type: type = str, converter: callable = None,
                 flag: bool = False, optional: bool = False, default: any = None, validator: callable = None):
        """
        Creates a command argument object
        :param name: the name (or names) of the argument
        :param description: a short description of the argument
        :param example: an example (string!) value for this argument
        :param type: the expected type of the argument
        :param converter: a converter function to convert the string value to the expected type
        :param flag: whether this argument should be treated as a flag
        :param optional: specifies if this argument is optional
        :param default: an optional default value
        :param validator: a validator function
        """
        for c in name:
            if c.isspace():
                raise ValueError("Argument name must not contain whitespace!")
        self.names = [name.strip()] if not isinstance(name, list) else name
        self.names = list(map(lambda x: x.strip(), self.names))
        self._validate_names()

        self.description = description.strip()
        self.example = example
        self.flag = flag
        self.type = bool if flag else type
        if converter is None:
            if self.type is str:
                self.converter = lambda x: x
            elif self.type is bool:
                self.converter = self._boolean_converter
            elif self.type is int:
                self.converter = lambda x: int(x)
            elif self.type is float:
                self.converter = self._float_converter
            else:
                raise ValueError("If you want to use a custom type, you have to provide a converter function too!")
        else:
            self.converter = converter
        self.optional = optional
        self.default = default
        self.validator = validator

    @property
    def name(self) -> str:
        return self.names[0]

    def parse_arg_value(self, arg: str) -> any:
        """
        Tries to parse the given value
        :param arg: the string value
        :return: the parsed value
        """
        if arg is None:
            if self.optional:
                return self.default
            else:
                raise ValueError("Missing required argument: '{}'".format(self.names[0]))

        parsed = self.converter(arg)
        if self.validator is not None:
            if not self.validator(parsed):
                raise ValueError("Invalid value for argument '{}': '{}'".format(self.names[0], arg))
        return parsed

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

    @staticmethod
    def _float_converter(value: str) -> float:
        """
        Converts a string to a float
        :param value: string value
        :return: float
        """
        if '%' == value[-1]:
            return float(value[:-1]) / 100.0
        else:
            return float(value)

    def _validate_names(self):
        """
        Validates argument names and raises an exception if something is invalid
        """
        for name in self.names:
            if ARG_VALUE_SEPARATOR_CHAR in name:
                raise ValueError("Argument names must not contain '=' character: {}".format(name))

        duplicates = find_duplicates(self.names)
        if len(duplicates) > 0:
            clashing = ", ".join(duplicates.keys())
            raise ValueError("Argument names must be unique! Clashing arguments: {}".format(clashing))


class Flag(Argument):
    """
    Convenience class for specifying a flag argument
    """

    def __init__(self, name: str or [str], description: str):
        """
        Creates a command argument object
        :param name: the name (or names) of the argument
        :param description: a short description of the argument
        """
        super().__init__(name, description, example="", type=bool, flag=True, optional=True, default=False)


class Selection(Argument):
    """
    Convenience class for a command argument based on a predefined selection of allowed values
    """

    def __init__(self, name: str, description: str, allowed_values: [any], type: type = str, converter: callable = None,
                 optional: bool = None, default: any = None):
        """
        Constructor
        :param name: the name of the argument
        :param description: a short description of the argument
        :param allowed_values: list of allowed (target type) values
        :param type: the expected type of the argument
        :param converter: a converter function to convert the string value to the expected type
        :param optional: specifies if this argument is optional
        :param default: an optional default value
        """
        self.allowed_values = allowed_values

        def validator(x):
            return x in self.allowed_values

        super().__init__(name, description, example=allowed_values[0], type=type, converter=converter,
                         optional=optional, default=default, validator=validator)
