# telegram-click ![https://badge.fury.io/py/telegram-click](https://badge.fury.io/py/telegram-click.svg) [![Build Status](https://travis-ci.org/markusressel/telegram-click.svg?branch=master)](https://travis-ci.org/markusressel/telegram-click)

[Click](https://github.com/pallets/click/) inspired command interface toolkit for [pyton-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).

![](/screenshots/demo.png)

# Features
* [x] POSIX style argument parsing
  * [x] Type conversion
    * [x] Custom type conversion support
  * [x] Input validation
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
        
    @command(name='age', description='Set age',
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

## Permission handling

If a command should only be executable when a specific criteria is met 
you can specify those criteria using the `permissions` parameter:

```python
from telegram import Update
from telegram.ext import CallbackContext
from telegram_click.decorator import command
from telegram_click.permission import GROUP_ADMIN

@command(name='permission', description='Needs permission',
         permissions=GROUP_ADMIN)
def _permission_command_callback(self, update: Update, context: CallbackContext):
    pass
```

Multiple permissions can be combined using `&`, `|` and `~` (not) operators.

If a user does not have permission to use a command it will not be displayed
when this user generate a list of commands.

### Integrated permission handlers

| Name                  | Description                                |
|-----------------------|--------------------------------------------|
| `PRIVATE_CHAT`        | Requires command execution inside of a private chat |
| `NORMAL_GROUP_CHAT`   | Requires command execution inside a normal group  |
| `SUPER_GROUP_CHAT`    | Requires command execution inside a supergroup  |
| `GROUP_CHAT`          | Requires command execution inside either a normal or supergroup |
| `USER_ID`             | Only allow users with a user id specified  |
| `USER_NAME`           | Only allow users with a username specified |
| `GROUP_CREATOR`       | Only allow the group creator               |
| `GROUP_ADMIN`         | Only allow the group admin                 |

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
    pass
```

### Show "Permission denied" message

By default command calls coming from a user without permission are ignored.
If you want to send them a "permission denied" like message you can 
pass this message to the `permission_denied_message` argument of the 
`@command` decorator.

## Error handling

**telegram-click** automatically handles errors when
 
* an argument can not be parsed correctly
* an invalid value is passed for an argument
* too many arguments are passed

In these cases the message of the internal exception is sent to the chat
along with a help message for the failed command.

**Note:**
This error handling does also handle errors that occur in your handler 
function and (by default) prints the exception text to the chat. If you 
don't want to send the exception message to the user set the `print_error`
parameter to `False`.

# Limitations

Currently the decorator expects a `classmethod` meaning the first 
parameter of it is the `self` parameter. This will probably be supported
in a future release.

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
