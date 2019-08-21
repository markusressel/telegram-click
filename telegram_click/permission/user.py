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

from telegram import Update
from telegram.ext import CallbackContext

from .base import Permission


class _Anybody(Permission):
    """
    Permission that is always True.
    """

    def evaluate(self, update: Update, context: CallbackContext) -> bool:
        return True


class _Nobody(Permission):
    """
    Permission that is never True.
    """

    def evaluate(self, update: Update, context: CallbackContext) -> bool:
        return False


class _UserId(Permission):
    """
    Requires that the command user has a specific user id.
    """

    def __init__(self, *id: int):
        self.ids = set(list(id))

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, " | ".join(list(map(str, self.ids))))

    def __repr__(self):
        return "<{}>".format(self.__str__())

    def evaluate(self, update: Update, context: CallbackContext) -> bool:
        from_user = update.effective_message.from_user
        return from_user.id in self.ids


class _UserName(Permission):
    """
    Requires that the command user has a specific username.
    """

    def __init__(self, *username: str):
        fixed_usernames = map(self._remove_at_if_present, set(username))
        self.usernames = set(filter(lambda x: x is not None, fixed_usernames))

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, " | ".join(self.usernames))

    def __repr__(self):
        return "<{}>".format(self.__str__())

    @staticmethod
    def _remove_at_if_present(x: str) -> str or None:
        result = x
        if result is None or not result.strip():
            return None

        if result.startswith("@"):
            result = result[1:]

        return result

    def evaluate(self, update: Update, context: CallbackContext) -> bool:
        from_user = update.effective_message.from_user
        return from_user.username in self.usernames


class _GroupCreator(Permission):
    """
    Requires that the command user is the group creator.
    """

    def evaluate(self, update: Update, context: CallbackContext) -> bool:
        bot = context.bot
        chat_id = update.effective_message.chat_id
        from_user = update.effective_message.from_user
        member = bot.getChatMember(chat_id, from_user.id)

        return member.status == "creator"


class _GroupAdmin(Permission):
    """
    Requires that the command user is a group admin.
    """

    def evaluate(self, update: Update, context: CallbackContext) -> bool:
        bot = context.bot
        chat_id = update.effective_message.chat_id
        from_user = update.effective_message.from_user
        member = bot.getChatMember(chat_id, from_user.id)

        return member.status == "administrator"
