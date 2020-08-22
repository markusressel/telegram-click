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

from telegram_click.argument import Argument, Flag
from telegram_click.parser import parse_telegram_command, split_into_tokens
from tests import TestBase


class ParserTest(TestBase):

    def test_flag(self):
        flag1 = Flag(
            name="flag",
            description="some flag description",
        )

        bot_username = "mybot"
        command_line = '/command --{}'.format(flag1.name)
        expected_args = [
            flag1,
        ]

        command, parsed_args = parse_telegram_command(bot_username, command_line, expected_args)

        self.assertEqual(command, "command")
        self.assertEqual(len(parsed_args), len(expected_args))
        self.assertTrue("flag" in parsed_args)
        self.assertTrue(parsed_args["flag"] is True)

    def test_multi_flag(self):
        flag1 = Flag(
            name=["flag", "f"],
            description="some flag description",
        )
        flag2 = Flag(
            name=["Flag", "F"],
            description="some flag description",
        )

        bot_username = "mybot"
        command_line = '/command --{}{}'.format(flag1.names[1], flag2.names[1])
        expected_args = [
            flag1,
            flag2,
        ]

        command, parsed_args = parse_telegram_command(bot_username, command_line, expected_args)

        self.assertEqual(command, "command")
        self.assertEqual(len(parsed_args), len(expected_args))
        self.assertTrue("flag" in parsed_args)
        self.assertTrue(parsed_args["flag"] is True)

    def test_flag_missing(self):
        flag1 = Flag(
            name="flag",
            description="some flag description",
        )

        bot_username = "mybot"
        command_line = '/command'.format(flag1.name)
        expected_args = [
            flag1,
        ]

        command, parsed_args = parse_telegram_command(bot_username, command_line, expected_args)

        self.assertEqual(command, "command")
        self.assertEqual(len(parsed_args), len(expected_args))
        self.assertTrue("flag" in parsed_args)
        self.assertTrue(parsed_args["flag"] is False)

    def test_excess_floating_args(self):
        flag1 = Argument(
            name="flag",
            description="some flag description",
            flag=True,
            example=""
        )

        bot_username = "mybot"
        command_line = '/command --{} 123 haha'.format(flag1.name)
        expected_args = [
            flag1,
        ]

        command, parsed_args = parse_telegram_command(bot_username, command_line, expected_args)

        self.assertEqual(command, "command")
        self.assertEqual(len(parsed_args), len(expected_args))
        self.assertTrue("flag" in parsed_args)
        self.assertTrue(parsed_args["flag"] is True)

    def test_excess_named_args(self):
        flag1 = Argument(
            name="flag",
            description="some flag description",
            flag=True,
            example=""
        )

        bot_username = "mybot"
        command_line = '/command hello --{} --fail 123'.format(flag1.name)
        expected_args = [
            flag1,
        ]

        self.assertRaises(ValueError, parse_telegram_command, bot_username, command_line, expected_args)

    def test_named_argument(self):
        arg1 = Argument(
            name="int_arg",
            description="str description",
            type=int,
            example="5"
        )
        arg2 = Argument(
            name="str_arg",
            description="str description",
            example="text"
        )
        arg3 = Argument(
            name="float_arg",
            description="str description",
            type=float,
            example="1.23",
            optional=True,
            default=12.5
        )

        bot_username = "mybot"
        command_line = '/command 12345 --{} "two words"'.format(arg2.name)
        expected_args = [
            arg1,
            arg2,
            arg3
        ]

        command, parsed_args = parse_telegram_command(bot_username, command_line, expected_args)

        self.assertEqual(command, "command")
        self.assertEqual(len(parsed_args), len(expected_args))
        self.assertEqual(parsed_args[arg1.name], 12345)
        self.assertEqual(parsed_args[arg2.name], "two words")
        self.assertEqual(parsed_args[arg3.name], arg3.default)

    def test_quote_within_quote(self):
        arg1 = Argument(
            name="a",
            description="str description",
            example="v"
        )
        arg_val = "te\'st"

        bot_username = "mybot"
        command_line = '/command "{}"'.format(arg_val)
        expected_args = [
            arg1
        ]

        command, parsed_args = parse_telegram_command(bot_username, command_line, expected_args)

        self.assertEqual(parsed_args[arg1.name], arg_val)

    def test_escape_char(self):
        arg1 = Argument(
            name="a",
            description="str description",
            example="v"
        )

        arg_values = [
            {
                "in": 'te\\"st',
                "out": 'te"st'
            },
            {
                "in": 'test\\"',
                "out": 'test"'
            }
        ]

        bot_username = "mybot"
        expected_args = [
            arg1
        ]

        for arg_val in arg_values:
            command_line = '/command "{}"'.format(arg_val["in"])
            command, parsed_args = parse_telegram_command(bot_username, command_line, expected_args)
            self.assertEqual(parsed_args[arg1.name], arg_val["out"])

    def test_naming_prefix_within_quote(self):
        arg1 = Argument(
            name="a",
            description="str description",
            example="v"
        )
        arg_val = "--a"

        bot_username = "mybot"
        command_line = '/command "{}"'.format(arg_val)
        expected_args = [
            arg1
        ]

        command, parsed_args = parse_telegram_command(bot_username, command_line, expected_args)

        self.assertEqual(parsed_args[arg1.name], arg_val)

    def test_token_splitting(self):
        args = [
            "abc",
            "\"double quoted with space\"",
            "\"'double quoted 'with single quote'\"",

            "'single quoted with space'",
            "'\"single quoted \"with double quote\"'",
        ]
        joined_args = " ".join(args)
        tokens = split_into_tokens(joined_args)

        for idx, arg in enumerate(args):
            self.assertEqual(arg, tokens[idx])

        double_test = "\"\\\"double quoted with \\\"escaped double quote\\\"\""
        self.assertIn("\"\"double quoted with \"escaped double quote\"\"", split_into_tokens(double_test))

        single_test = "'\\'single quoted with \\'escaped single quote\\''"
        self.assertIn("''single quoted with 'escaped single quote''", split_into_tokens(single_test))
