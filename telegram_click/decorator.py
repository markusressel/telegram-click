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

import functools
import logging

from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from telegram_click import CommandTarget
from telegram_click.argument import Argument
from telegram_click.help import generate_help_message
from telegram_click.parser import parse_telegram_command, split_command_from_args, split_command_from_target
from telegram_click.permission.base import Permission
from telegram_click.util import send_message, find_first, find_duplicates

LOGGER = logging.getLogger(__name__)


def _check_permissions(update: Update, context: CallbackContext,
                       permissions: Permission) -> bool:
    """
    Checks if a message passes permission tests
    :param update: message update
    :param context: message context
    :param permissions: command permissions
    :return: True if authorized, False otherwise
    """
    if permissions is not None:
        return permissions.evaluate(update, context)
    else:
        return True


def _create_callback_wrapper(func: callable, help_message: str,
                             arguments: [Argument],
                             permissions: Permission, permission_denied_message: str or None,
                             command_target: bytes,
                             print_error: bool) -> callable:
    """
    Creates the wrapper function for the callback function
    :param func: the function to wrap
    :param help_message: command help message
    :param arguments: command arguments
    :param permissions: command permissions
    :param permission_denied_message: permission denied message
    :param command_target: command target
    :param print_error: True prints the exception stacktrace, False a general error message
    :return: wrapper function
    """
    if not callable(func):
        raise AttributeError("Unsupported type: {}".format(func))

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # find function arguments
        update = find_first(args, Update)
        context = find_first(args, CallbackContext)

        # get bot, chat and message info
        bot = context.bot
        message = update.effective_message
        chat_id = message.chat_id

        try:
            if not _check_permissions(update, context, permissions):
                LOGGER.debug("Permission denied in chat {} for user {} for message: {}".format(
                    chat_id,
                    update.effective_message.from_user.id,
                    message))

                # send 'permission denied' message, if configured
                if permission_denied_message is not None:
                    send_message(bot, chat_id=chat_id, message=permission_denied_message,
                                 parse_mode=ParseMode.MARKDOWN,
                                 reply_to=message.message_id)
                # don't process command
                return

            # parse and check command target
            cmd, _ = split_command_from_args(message.text)
            _, target = split_command_from_target(bot.username, cmd)
            # check if we are allowed to process the given command target
            if not filter_command_target(target, bot.username, command_target):
                LOGGER.debug("Ignoring command for unspecified target {} in chat {} for user {}: {}".format(
                    target,
                    chat_id,
                    update.effective_message.from_user.id,
                    message))

                # don't process command
                return

            try:
                # parse command and arguments
                cmd, parsed_args = parse_telegram_command(bot.username, message.text, arguments)
            except ValueError as ex:
                # handle exceptions that occur during permission and argument parsing
                logging.exception("Error parsing command arguments")

                denied_text = "\n".join([
                    ":exclamation: `{}`".format(str(ex)),
                    "",
                    help_message
                ])
                send_message(bot, chat_id=chat_id, message=denied_text, parse_mode=ParseMode.MARKDOWN,
                             reply_to=message.message_id)
                return

            # convert argument names to python param naming convention (snake-case)
            kw_function_args = dict(map(lambda x: (x[0].lower().replace("-", "_"), x[1]), list(parsed_args.items())))
            # execute wrapped function
            return func(*args, **{**kw_function_args, **kwargs})
        except Exception as ex:
            # execute wrapped function
            logging.exception("Error in callback")

            import traceback
            exception_text = "\n".join(list(map(lambda x: "{}:{}\n\t{}".format(x.filename, x.lineno, x.line),
                                                traceback.extract_tb(ex.__traceback__))))
            if print_error:
                denied_text = ":boom: `{}`".format(exception_text)
            else:
                denied_text = ":boom: There was an error executing your command :worried:"
            send_message(bot, chat_id=chat_id, message=denied_text, parse_mode=ParseMode.MARKDOWN,
                         reply_to=message.message_id)

    return wrapper


def check_command_name_clashes(names: [str]):
    """
    Checks if a command name has been used multiple times and raises an exception if so
    :param names: command names added in this decorator call
    """
    from telegram_click import COMMAND_LIST

    t = []
    t.extend(map(lambda x: x["names"], COMMAND_LIST))
    t.extend([names])
    t = functools.reduce(list.__add__, t)

    duplicates = find_duplicates(t)
    if len(duplicates) > 0:
        clashing = ", ".join(duplicates.keys())
        raise ValueError("Command names must be unique! Clashing names: {}".format(clashing))


def check_argument_name_clashes(arguments: []):
    """
    Checks if an argument name of a command has been used multiple times and raises an exception if so
    :param arguments: arguments of a command to check
    """
    duplicates = find_duplicates(list(map(lambda x: x.name, arguments)))
    if len(duplicates) > 0:
        clashing = ", ".join(duplicates.keys())
        raise ValueError("Argument names must be unique per command! Clashing arguments: {}".format(clashing))


def command(name: str or [str], description: str = None,
            arguments: [Argument] = None,
            permissions: Permission = None,
            permission_denied_message: str = None,
            command_target: bytes = CommandTarget.UNSPECIFIED | CommandTarget.SELF,
            print_error: bool = False):
    """
    Decorator to turn a command handler function into a full fledged, shell like command
    :param name: Name of the command
    :param description: a short description of the command
    :param arguments: list of command argument description objects
    :param permissions: required permissions to run this command
    :param permission_denied_message: text so send when a user is denied permission.
                                      Set this to None to send no message at all.
    :param command_target: command targets to accept
    :param print_error: True sends the exception message to the chat of origin,
                        False sends a general error message
    """
    from telegram_click import COMMAND_LIST

    name = [name] if not isinstance(name, list) else name
    if arguments is None:
        arguments = []

    check_command_name_clashes(name)
    check_argument_name_clashes(arguments)

    help_message = generate_help_message(name, description, arguments)

    COMMAND_LIST.append(
        {
            "names": name,
            "description": description,
            "arguments": arguments,
            "message": help_message,
            "permissions": permissions
        }
    )

    def callback_decorator(func: callable):
        """
        Callback decorator function
        :param func: the function to wrap
        :return: wrapper function
        """
        return _create_callback_wrapper(func, help_message, arguments, permissions, permission_denied_message,
                                        command_target, print_error)

    return callback_decorator


def filter_command_target(target: str or None, bot_username: str, allowed_targets: bytes):
    """
    Checks if the command target should be accepted based on given input
    :param target: the target of the command or None
    :param bot_username: the username of this bot
    :param allowed_targets: the allowed command target bitmask
    :return: True if allowed, False if not
    """
    if target is None:
        expected = CommandTarget.UNSPECIFIED
    elif target == bot_username:
        expected = CommandTarget.SELF
    else:
        expected = CommandTarget.OTHER

    return expected & allowed_targets == expected
