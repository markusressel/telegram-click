# telegram-click ![https://badge.fury.io/py/telegram-click](https://badge.fury.io/py/telegram-click.svg)

Click inspired command interface toolkit for pyton-telegram-bot.

![](/screenshots/demo.png)

# Features
* [x] Help message generation
* [x] Argument parsing, type conversion and validation
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
[...]
from telegram_click import command, generate_command_list
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
If you want to use other types you have to specify how the sctring input
can be converted to your type using the `converter` attribute of the 
`Argument` constructor like so:

```python
 Argument(name='age',
          description='The new age',
          type=MyType,
          converter=lambda x: MyType(x),
          validator=lambda x: x > 0,
          example='25')
```

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