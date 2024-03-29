from telegram import Update
from telegram.ext import ContextTypes

from telegram_click.permission.base import Permission
from telegram_click.util import send_message


class ErrorHandler:
    """
    Interface for error handlers
    """

    async def on_permission_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  permissions: Permission) -> bool:
        """
        This method is called when a user tries to execute a command without permission
        :param update: Message Update
        :param context: Callback context
        :param permissions: the permissions, at least one of which was missing
        :return: True if the error was handled, false otherwise
        """
        return False

    async def on_validation_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE, exception: Exception,
                                  help_message: str) -> bool:
        """
        This method is called when an exception is raised during
        argument user input validation.
        :param update: Message Update
        :param context: Callback context
        :param exception: the exception
        :param help_message: help message for the command that failed validation
        :return: True if the error was handled, false otherwise
        """
        return False

    async def on_execution_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                 exception: Exception) -> bool:
        """
        This method is called when an exception is raised during
        the execution of a command
        :param update: Message Update
        :param context: Callback context
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

    async def on_permission_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  permissions: Permission) -> bool:
        bot = context.bot
        message = update.effective_message
        chat_id = message.chat_id

        if not self.silent_denial:
            # send 'permission denied' message
            text = self.DEFAULT_PERMISSION_DENIED_MESSAGE
            await send_message(bot, chat_id=chat_id, message=text,
                               parse_mode="MARKDOWN",
                               reply_to=message.message_id)

        return True

    async def on_validation_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE, exception: Exception,
                                  help_message: str) -> bool:
        bot = context.bot
        message = update.effective_message
        chat_id = message.chat_id

        denied_text = "\n".join([
            ":exclamation: `{}`".format(str(exception)),
            "",
            help_message
        ])
        await send_message(bot, chat_id=chat_id,
                           message=denied_text,
                           parse_mode="MARKDOWN",
                           reply_to=message.message_id)
        return True

    async def on_execution_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                 exception: Exception) -> bool:
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
        await send_message(bot, chat_id=chat_id,
                           message=denied_text,
                           parse_mode="MARKDOWN",
                           reply_to=message.message_id)
        return True


DEFAULT_ERROR_HANDLER = DefaultErrorHandler()
