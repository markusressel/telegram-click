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

from telegram import Update
from telegram.ext import CallbackContext

from .base import Permission


class GroupAdmin(Permission):
    """
    Requires the user that executes the command to be the creator or admin of the chat.
    If the chat is a private chat this is always true.
    """

    def evaluate(self, update: Update, context: CallbackContext, command: str) -> bool:
        bot = context.bot
        chat_id = update.effective_message.chat_id
        from_user = update.effective_message.from_user
        chat_type = update.effective_chat.type
        member = bot.getChatMember(chat_id, from_user.id)

        if chat_type == 'private':
            return True

        return member.status == "administrator" or member.status == "creator"
