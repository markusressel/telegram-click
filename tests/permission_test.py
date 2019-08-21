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

import datetime

from telegram import Update
from telegram.ext import CallbackContext

from telegram_click.permission.base import Permission
from tests import TestBase


class TruePermission(Permission):
    def evaluate(self, update: Update, context: CallbackContext):
        return True


class FalsePermission(Permission):
    def evaluate(self, update: Update, context: CallbackContext):
        return False


def _create_update_mock(chat_id: int = -12345678, chat_type: str = "private", message_id: int = 12345678,
                        user_id: int = 12345678, username: str = "myusername") -> Update:
    """
    Helper method to create an "Update" object with mocked content
    """
    import telegram

    update = lambda: None  # type: Update

    user = telegram.User(
        id=user_id,
        username=username,
        first_name="Max",
        is_bot=False
    )

    chat = telegram.Chat(id=chat_id, type=chat_type)
    date = datetime.datetime.now()

    update.effective_chat = chat
    update.effective_message = telegram.Message(
        message_id=message_id,
        from_user=user,
        chat=chat,
        date=date,
    )

    return update


class PermissionTest(TestBase):

    @staticmethod
    def test_permission_nobody():
        from telegram_click.permission import NOBODY
        permission = NOBODY

        update = None
        context = None

        assert not permission.evaluate(update, context)

    @staticmethod
    def test_permission_username():
        from telegram_click.permission import USER_NAME
        permission = USER_NAME("markusressel")

        valid_update = _create_update_mock(username="markusressel")
        assert permission.evaluate(valid_update, None)

        invalid_update = _create_update_mock(username="markus")
        assert not permission.evaluate(invalid_update, None)

        invalid_update = _create_update_mock(username="other")
        assert not permission.evaluate(invalid_update, None)

        invalid_update = _create_update_mock(username=None)
        assert not permission.evaluate(invalid_update, None)

    @staticmethod
    def test_permission_user_id():
        from telegram_click.permission import USER_ID
        permission = USER_ID(12345678)

        valid_update = _create_update_mock(user_id=12345678)
        assert permission.evaluate(valid_update, None)

        invalid_update = _create_update_mock(user_id=87654321)
        assert not permission.evaluate(invalid_update, None)

    @staticmethod
    def test_permission_merged_and():
        merged_permission = FalsePermission() & FalsePermission()
        assert not merged_permission.evaluate(None, None)
        merged_permission = TruePermission() & FalsePermission()
        assert not merged_permission.evaluate(None, None)
        merged_permission = FalsePermission() & TruePermission()
        assert not merged_permission.evaluate(None, None)
        merged_permission = TruePermission() & TruePermission()
        assert merged_permission.evaluate(None, None)

    @staticmethod
    def test_permission_merged_or():
        merged_permission = FalsePermission() | FalsePermission()
        assert not merged_permission.evaluate(None, None)
        merged_permission = TruePermission() | FalsePermission()
        assert merged_permission.evaluate(None, None)
        merged_permission = FalsePermission() | TruePermission()
        assert merged_permission.evaluate(None, None)
        merged_permission = TruePermission() | TruePermission()
        assert merged_permission.evaluate(None, None)

    @staticmethod
    def test_permission_not():
        not_permission = ~ TruePermission()
        assert not not_permission.evaluate(None, None)
        not_permission = ~ FalsePermission()
        assert not_permission.evaluate(None, None)
