# telegram-click [![Contributors](https://img.shields.io/github/contributors/markusressel/telegram-click.svg)](https://github.com/markusressel/telegram-click/graphs/contributors) [![MIT License](https://img.shields.io/github/license/markusressel/telegram-click.svg)](/LICENSE) ![Code Size](https://img.shields.io/github/languages/code-size/markusressel/telegram-click.svg) ![Latest Version](https://badge.fury.io/py/telegram-click.svg) [![Build Status](https://travis-ci.org/markusressel/telegram-click.svg?branch=master)](https://travis-ci.org/markusressel/telegram-click)

[Click](https://github.com/pallets/click/) 
inspired command-line interface creation toolkit for 
[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).

Try the latest version of the [example.py](/example.py) out for yourself: [@PythonTelegramClickBot](http://t.me/PythonTelegramClickBot)

<p align="center">
  <img src="/screenshots/demo1.png" width="400"> <img src="/screenshots/demo2.png" width="400"> <img src="/screenshots/demo3.png" width="400"> 
</p>

# Features
* [x] POSIX style argument parsing
  * [x] Quoted arguments (`/command "Hello World"`)
  * [x] Named arguments (`/command --text "Hello World"`)
  * [x] Flags (`/command --yes`)
  * [x] Optional arguments
  * [x] Type conversion including support for custom types
  * [x] Argument input validation
* [x] Automatic help messages
  * [x] Show help messages when a command was used with invalid arguments
  * [x] List all available commands with a single method
* [x] Permission handling
  * [x] Set up permissions for each command separately
  * [x] Limit command execution to private chats or group admins
  * [x] Combine permissions using logical operators
  * [x] Create custom permission handlers
* [x] Error handling
  * [x] Automatically send error messages if something goes wrong
  * [x] Optionally send exception messages
  
**telegram-click** is used by

* [InfiniteWisdom](https://github.com/ekeih/InfiniteWisdom)
* [DeineMudda](https://github.com/markusressel/DeineMudda)
* [grocy-telegram-bot](https://github.com/markusressel/grocy-telegram-bot)

and hopefully many others :)

# How to use

Install this library as a dependency to use it in your project.

```shell
pip install telegram-click
```

Then annotate your command handler functions with the `@command` decorator
of this library:

```python
from telegram import Update
from telegram.ext import CallbackContext
from telegram_click.decorator import command
from telegram_click.argument import Argument

class MyBot:

    [...]
    
    @command(name='start', description='Start bot interaction')
    def _start_command_callback(self, update: Update, context: CallbackContext):
        # do something
        pass
        
    @command(name='age', 
             description='Set age',
             arguments=[
                 Argument(name='age',
                          description='The new age',
                          type=int,
                          validator=lambda x: x > 0,
                          example='25')
             ])
    def _age_command_callback(self, update: Update, context: CallbackContext, age: int):
        context.bot.send_message(update.effective_chat.id, "New age: {}".format(age))
```

## Arguments

**telegram-click** automatically parses arguments based on 
[shlex POSIX rules](https://docs.python.org/3/library/shlex.html#parsing-rules)
so in general space acts as an argument delimiter and quoted arguments 
are parsed as a single one (supporting both double (`"`) and 
single (`'`) quote characters).

### Naming

Arguments can have multiple names to allow for abbreviated names. The
first name you specify for an argument will be used for the 
callback parameter name (normalized to snake-case). Because of this
it is advisable to specify the full argument name as the first one.

### Types

Since all user input initially is of type `str` there needs to be a type
conversion if the expected type is not a `str`. For basic types like
`bool`, `int`, `float` and `str` converters are built in to this library.
If you want to use other types you have to specify how to convert the 
`str` input to your type using the `converter` attribute of the 
`Argument` constructor:

```python
from telegram_click.argument import Argument

Argument(name='age',
         description='The new age',
         type=MyType,
         converter=lambda x: MyType(x),
         validator=lambda x: x > 0,
         example='25')
```

### Flags

Technically you can use the `Argument` class to specify a flag, but since 
many of its parameters are implicit for a flag the `Flag` class can be used
instead:

```python
from telegram_click.argument import Flag

Flag(name='flag',
     description='My boolean flag')
```

## Permission handling

If a command should only be executable when a specific criteria is met 
you can specify those criteria using the `permissions` parameter:

```python
from telegram import Update
from telegram.ext import CallbackContext
from telegram_click.decorator import command
from telegram_click.permission import GROUP_ADMIN

@command(name='permission', 
         description='Needs permission',
         permissions=GROUP_ADMIN)
def _permission_command_callback(self, update: Update, context: CallbackContext):
```

Multiple permissions can be combined using `&`, `|` and `~` (not) operators.

If a user does not have permission to use a command it will not be displayed
when this user generate a list of commands.

### Integrated permission handlers

| Name                  | Description                                |
|-----------------------|--------------------------------------------|
| `PRIVATE_CHAT`        | The command can only be executed in a private chat |
| `NORMAL_GROUP_CHAT`   | The command can only be executed in a normal group  |
| `SUPER_GROUP_CHAT`    | The command can only be executed in a supergroup  |
| `GROUP_CHAT`          | The command can only be executed in either a normal or a supergroup |
| `USER_ID`             | Only users whose user id is specified have permission |
| `USER_NAME`           | Only users whose username is specified have permission |
| `GROUP_CREATOR`       | Only the group creator has permission               |
| `GROUP_ADMIN`         | Only the group admin has permission                 |
| `NOBODY`              | Nobody has permission (useful for callbacks triggered via code instead of user interaction f.ex. "unknown command" handler) |
| `ANYBODY`             | Anybody has permission (this is the default) |

### Custom permission handler

If none of the integrated handlers suit your needs you can simply write 
your own permission handler by extending the `Permission` base class 
and pass an instance of the `MyPermission` class to the list of `permissions`:

```python
from telegram import Update
from telegram.ext import CallbackContext
from telegram_click.decorator import command
from telegram_click.permission.base import Permission
from telegram_click.permission import GROUP_ADMIN

class MyPermission(Permission):
    def evaluate(self, update: Update, context: CallbackContext) -> bool:
        from_user = update.effective_message.from_user
        return from_user.id in [12345, 32435]
        
@command(name='permission', description='Needs permission',
         permissions=MyPermission() & GROUP_ADMIN)
def _permission_command_callback(self, update: Update, context: CallbackContext):
```

### Show "Permission denied" message

By default command calls coming from a user without permission are ignored.
If you want to send them a "permission denied" like message you can 
pass this message to the `permission_denied_message` argument of the 
`@command` decorator.

## Targeted commands

Telegram supports the `@` notation to target commands at specific bot
usernames:

```
/start               # unspecified
/start@myAwesomeBot  # targeted at self
/start@someOtherBot  # targeted at other bot
```

When using a `MessageHandler` instead of a `CommandHandler`
it is possible to catch even commands that are targeted at other bots.
By default only messages without a target, and messages that are targeted 
directly at your bot are processed.

To control this behaviour specify the `command_target` parameter:

```python
from telegram import Update
from telegram.ext import CallbackContext
from telegram_click.decorator import command
from telegram_click import CommandTarget
from telegram_click.permission import NOBODY

@command(name="commands",
         description="List commands supported by this bot.",
         permissions=NOBODY,
         command_target=CommandTarget.UNSPECIFIED | CommandTarget.SELF)
def _unknown_command_callback(self, update: Update, context: CallbackContext):
```

You can combine `CommandTarget`'s using logical operators like in the 
example above.

## Error handling

**telegram-click** automatically handles errors in most situations.

When an exception is raised the user will be notified that his 
command has crashed the server. By default he will only see
a general error message. If you want to send full stacktraces 
instead, set the `print_error` parameter to `True`.

The user is also informed about input errors like
* an argument can not be parsed correctly
* an invalid value is passed for an argument
In these cases the user will get a more specific error message
and a help message for the command he was trying to use.

# Contributing

GitHub is for social coding: if you want to write code, I encourage contributions through pull requests from forks
of this repository. Create GitHub tickets for bugs and new features and comment on the ones that you are interested in.


# License
```text
telegram-click
Copyright (c) 2019 Markus Ressel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
