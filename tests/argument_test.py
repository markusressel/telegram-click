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

from telegram_click.argument import Argument
from tests import TestBase


class ArgumentTest(TestBase):

    def test_str_argument(self):
        arg = Argument(
            name="str_arg",
            description="str description",
            example="text"
        )

        self.assertEqual(arg.parse_arg_value("sample"), "sample")

    def test_bool_argument(self):
        arg = Argument(
            name="boolean_arg",
            description="boolean description",
            type=bool,
            example="0"
        )

        self.assertFalse(arg.parse_arg_value("0"))

    def test_int_argument(self):
        arg = Argument(
            name="int_arg",
            description="int description",
            type=int,
            example="0"
        )

        self.assertEqual(arg.parse_arg_value("0"), 0)
        self.assertEqual(arg.parse_arg_value("01"), 1)
        self.assertEqual(arg.parse_arg_value("10"), 10)

    def test_float_argument(self):
        arg = Argument(
            name="float_arg",
            description="float description",
            type=float,
            example="1.2"
        )

        self.assertEqual(arg.parse_arg_value("0"), 0.0)
        self.assertEqual(arg.parse_arg_value("01"), 1.0)
        self.assertEqual(arg.parse_arg_value("10"), 10.0)
        self.assertEqual(arg.parse_arg_value("10.2"), 10.2)
        self.assertEqual(arg.parse_arg_value("3%"), 0.03)
