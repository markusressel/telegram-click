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
from telegram_click import CommandTarget
from telegram_click.decorator import filter_command_target
from tests import TestBase


class CommandTargetTest(TestBase):

    @staticmethod
    def test_target_self():
        bot_name = "myBot"

        assert filter_command_target(bot_name, bot_name, CommandTarget.SELF)
        assert not filter_command_target(bot_name, bot_name, CommandTarget.UNSPECIFIED)
        assert not filter_command_target(bot_name, bot_name, CommandTarget.OTHER)
        assert filter_command_target(bot_name, bot_name, CommandTarget.ANY)

    @staticmethod
    def test_target_other():
        bot_name = "myBot"
        other_bot_name = "otherBot"

        assert not filter_command_target(other_bot_name, bot_name, CommandTarget.SELF)
        assert not filter_command_target(other_bot_name, bot_name, CommandTarget.UNSPECIFIED)
        assert filter_command_target(other_bot_name, bot_name, CommandTarget.OTHER)
        assert filter_command_target(other_bot_name, bot_name, CommandTarget.ANY)

    @staticmethod
    def test_target_unspecified():
        bot_name = "myBot"

        assert not filter_command_target(None, bot_name, CommandTarget.SELF)
        assert filter_command_target(None, bot_name, CommandTarget.UNSPECIFIED)
        assert not filter_command_target(None, bot_name, CommandTarget.OTHER)
        assert filter_command_target(None, bot_name, CommandTarget.ANY)
