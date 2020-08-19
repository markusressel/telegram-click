from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from telegram_click.permission.base import Permission
from telegram_click.util import send_message


class ErrorHandler:
    """
    Interface for error handlers
    """

    def on_permission_error(self, context: CallbackContext, update: Update, permissions: Permission) -> bool:
        """
        This method is called when a user tries to execute a command without permission
        :param context: Callback context
        :param update: Message Update
        :param permissions: the permissions, at least one of which was missing
        :return: True if the error was handled, false otherwise
        """
        return False

    def on_validation_error(self, context: CallbackContext, update: Update, exception: Exception,
                            help_message: str) -> bool:
        """
        This method is called when an exception is raised during
        argument user input validation.
        :param context: Callback context
        :param update: Message Update
        :param exception: the exception
        :param help_message: help message for the command that failed validation
        :return: True if the error was handled, false otherwise
        """
        return False

    def on_execution_error(self, context: CallbackContext, update: Update, exception: Exception) -> bool:
        """
        This method is called when an exception is raised during
        the execution of a command
        :param context: Callback context
        :param update: Message Update
        :param exception: the exception
        :return: true if the error was handled, false otherwise
        """
        return False


class DefaultErrorHandler(ErrorHandler):
    DEFAULT_PERMISSION_DENIED_MESSAGE = ":stop_sign: You do not have permission to use this command."

    def __init__(self, silent_denial: bool = True, print_error: bool = False):
        """
        Creates an instance
        :param silent_denial: Whether to silently ignore commands from users without permission
        :param print_error: Whether to print a stacktrace on execution errors
        """
        self.silent_denial = silent_denial
        self.print_error = print_error

    def on_permission_error(self, context: CallbackContext, update: Update, permissions: Permission) -> bool:
        bot = context.bot
        message = update.effective_message
        chat_id = message.chat_id

        if not self.silent_denial:
            # send 'permission denied' message
            text = self.DEFAULT_PERMISSION_DENIED_MESSAGE
            send_message(bot, chat_id=chat_id, message=text,
                         parse_mode=ParseMode.MARKDOWN,
                         reply_to=message.message_id)

        return True

    def on_validation_error(self, context: CallbackContext, update: Update, exception: Exception,
                            help_message: str) -> bool:
        bot = context.bot
        message = update.effective_message
        chat_id = message.chat_id

        denied_text = "\n".join([
            ":exclamation: `{}`".format(str(exception)),
            "",
            help_message
        ])
        send_message(bot, chat_id=chat_id,
                     message=denied_text,
                     parse_mode=ParseMode.MARKDOWN,
                     reply_to=message.message_id)
        return True

    def on_execution_error(self, context: CallbackContext, update: Update, exception: Exception) -> bool:
        bot = context.bot
        message = update.effective_message
        chat_id = message.chat_id

        if self.print_error:
            import traceback
            exception_text = "\n".join(list(map(lambda x: "{}:{}\n\t{}".format(x.filename, x.lineno, x.line),
                                                traceback.extract_tb(exception.__traceback__))))
            denied_text = ":boom: `{}`".format(exception_text)
        else:
            denied_text = ":boom: There was an error executing your command :worried:"
        send_message(bot, chat_id=chat_id,
                     message=denied_text,
                     parse_mode=ParseMode.MARKDOWN,
                     reply_to=message.message_id)
        return True


DEFAULT_ERROR_HANDLER = DefaultErrorHandler()
