# telegram-click ![https://badge.fury.io/py/telegram-click](https://badge.fury.io/py/telegram-click.svg)

Click inspired command interface toolkit for pyton-telegram-bot.

![](/screenshots/demo.png)

# Features
* [x] Help message generation
* [x] Argument parsing, type conversion and validation
* [x] Permission handling
* [x] Error handling

# How to use

Install this library as a dependency to use it in your project.

```shell
pip install telegram-click
```

Then annotate your command handler functions with the `@command` decorator
of this library. The information you need to provide is used to generate
the help messages.

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

## Custom types

Since all user input initially is of type `str` there needs to be a type
conversion if the expected type is a different one. For basic types like
`bool`, `int`, `float` and `str` converters are built in to this library.
If you want to use other types you have to specify how the string input
can be converted to your type using the `converter` attribute of the 
`Argument` constructor like so:

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
         permissions=[
            GROUP_ADMIN
         ])
def _permission_command_callback(self, update: Update, context: CallbackContext, age: int):
    pass
```

### Custom permission handler

If none of the integrated handlers suit your needs you can simply write 
your own permission handler by extending the `Permission` base class 
and pass an instance of the `MyPermission` class to the list of `permissions`:

```python
from telegram import Update
from telegram.ext import CallbackContext
from telegram_click.decorator import command
from telegram_click.permission.base import Permission

class MyPermission(Permission):
    def evaluate(self, update: Update, context: CallbackContext, command: str) -> bool:
        from_user = update.effective_message.from_user
        return from_user.id in [12345, 32435]
        
@command(name='permission', description='Needs permission',
         permissions=[
            MyPermission()
         ])
def _permission_command_callback(self, update: Update, context: CallbackContext, age: int):
    pass
```

## Error handling

**telegram-click** automatically handles errors when
 
* an argument can not be parsed correctly
* an invalid value is passed for an argument
* too many arguments are passed

In these cases the message of the internal exception is sent to the chat
along with a help message for the failed command.

**Note:**
This error handling does not handle errors that occur in your handler 
function but only command argument related ones.

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