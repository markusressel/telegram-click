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

    def test_permission_nobody(self):
        from telegram_click.permission import NOBODY
        permission = NOBODY

        update = None
        context = None

        self.assertFalse(permission.evaluate(update, context))

    def test_permission_username(self):
        from telegram_click.permission import USER_NAME
        permission = USER_NAME("markusressel")

        valid_update = _create_update_mock(username="markusressel")
        self.assertTrue(permission.evaluate(valid_update, None))

        invalid_update = _create_update_mock(username="markus")
        self.assertFalse(permission.evaluate(invalid_update, None))

        invalid_update = _create_update_mock(username="other")
        self.assertFalse(permission.evaluate(invalid_update, None))

        invalid_update = _create_update_mock(username=None)
        self.assertFalse(permission.evaluate(invalid_update, None))

    def test_permission_user_id(self):
        from telegram_click.permission import USER_ID
        permission = USER_ID(12345678)

        valid_update = _create_update_mock(user_id=12345678)
        self.assertTrue(permission.evaluate(valid_update, None))

        invalid_update = _create_update_mock(user_id=87654321)
        self.assertFalse(permission.evaluate(invalid_update, None))

    def test_permission_merged_and(self):
        merged_permission = FalsePermission() & FalsePermission()
        self.assertFalse(merged_permission.evaluate(None, None))
        merged_permission = TruePermission() & FalsePermission()
        self.assertFalse(merged_permission.evaluate(None, None))
        merged_permission = FalsePermission() & TruePermission()
        self.assertFalse(merged_permission.evaluate(None, None))
        merged_permission = TruePermission() & TruePermission()
        self.assertTrue(merged_permission.evaluate(None, None))

    def test_permission_merged_or(self):
        merged_permission = FalsePermission() | FalsePermission()
        self.assertFalse(merged_permission.evaluate(None, None))
        merged_permission = TruePermission() | FalsePermission()
        self.assertTrue(merged_permission.evaluate(None, None))
        merged_permission = FalsePermission() | TruePermission()
        self.assertTrue(merged_permission.evaluate(None, None))
        merged_permission = TruePermission() | TruePermission()
        self.assertTrue(merged_permission.evaluate(None, None))

    def test_permission_not(self):
        not_permission = ~ TruePermission()
        self.assertFalse(not_permission.evaluate(None, None))
        not_permission = ~ FalsePermission()
        self.assertTrue(not_permission.evaluate(None, None))
