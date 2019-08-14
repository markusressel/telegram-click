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
from telegram_click.permission.base import Permission
from telegram_click.util import generate_help_message, parse_telegram_command, send_message, find_first

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


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
    :param print_error:
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

        # parse command and arguments
        target, command, string_arguments = parse_telegram_command(bot.username, message.text)

        # check if we are allowed to process the given command target
        if not filter_command_target(target, bot.username, command_target):
            return

        parsed_args = []
        try:
            # check permissions
            if permissions is not None:
                if not permissions.evaluate(update, context):
                    raise PermissionError("You do not have permission to use this command")

            # check argument count
            if len(string_arguments) > len(arguments):
                raise ValueError("Too many arguments!")

            # try to convert arguments
            for idx, arg in enumerate(arguments):
                try:
                    string_arg = string_arguments[idx]
                except IndexError:
                    string_arg = None

                if string_arg is None:
                    if arg.default is not None:
                        parsed = arg.default
                    else:
                        raise ValueError("Missing value for argument: {}".format(arg.name))
                else:
                    parsed = arg.parse_arg(string_arg)

                parsed_args.append(parsed)
        except PermissionError as ex:
            # send permission error (if configured)
            LOGGER.debug("Permission error in chat {} from user {}: {}".format(chat_id,
                                                                               update.effective_message.from_user.id,
                                                                               ex))
            if permission_denied_message is None:
                return

            send_message(bot, chat_id=chat_id, message=permission_denied_message,
                         parse_mode=ParseMode.MARKDOWN,
                         reply_to=message.message_id)
            return
        except Exception as ex:
            # handle exceptions that occur during permission and argument parsing
            LOGGER.error(ex)

            import traceback
            exception_text = "\n".join(list(map(lambda x: "{}:{}\n\t{}".format(x.filename, x.lineno, x.line),
                                                traceback.extract_tb(ex.__traceback__))))

            denied_text = "\n".join([
                ":exclamation: `{}`".format(str(ex)),
                "",
                help_message
            ])
            send_message(bot, chat_id=chat_id, message=denied_text, parse_mode=ParseMode.MARKDOWN,
                         reply_to=message.message_id)
            return

        try:
            # execute wrapped function
            return func(*args, *parsed_args, **kwargs)
        except Exception as ex:
            # execute wrapped function
            LOGGER.error(ex)

            import traceback
            exception_text = "\n".join(list(map(lambda x: "{}:{}\n\t{}".format(x.filename, x.lineno, x.line),
                                                traceback.extract_tb(ex.__traceback__))))
            if print_error:
                denied_text = ":boom: `{}`".format(str(ex))
            else:
                denied_text = "There was an error executing your command :worried:"
            send_message(bot, chat_id=chat_id, message=denied_text, parse_mode=ParseMode.MARKDOWN,
                         reply_to=message.message_id)

    return wrapper


def command(name: str, description: str = None,
            arguments: [Argument] = None,
            permissions: Permission = None,
            permission_denied_message: str = None,
            command_target: bytes = CommandTarget.UNSPECIFIED | CommandTarget.SELF,
            print_error: bool = True):
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
    if arguments is None:
        arguments = []

    help_message = generate_help_message(name, description, arguments)

    from telegram_click import COMMAND_LIST
    COMMAND_LIST.append(
        {
            "name": name,
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
