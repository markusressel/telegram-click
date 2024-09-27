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
#

from setuptools import setup, find_packages

VERSION_NUMBER = "6.0.3"

DEVELOPMENT_STATUS = "Development Status :: 5 - Production/Stable"
VERSION_NAME = VERSION_NUMBER


def readme_type() -> str:
    import os
    if os.path.exists("README.rst"):
        return "text/x-rst"
    if os.path.exists("README.md"):
        return "text/markdown"


def readme() -> [str]:
    if readme_type() == "text/markdown":
        file_name = "README.md"
    else:
        file_name = "README.rst"

    with open(file_name) as f:
        return f.read()


def locked_requirements(section):
    """
    Look through the 'Pipfile.lock' to fetch requirements by section.
    """
    import json

    with open('Pipfile.lock') as pip_file:
        pipfile_json = json.load(pip_file)

    if section not in pipfile_json:
        print("{0} section missing from Pipfile.lock".format(section))
        return []

    return [package
            for package, detail in pipfile_json[section].items()]


setup(
    name='telegram_click',
    version=VERSION_NAME,
    description='Click inspired command interface toolkit for pyton-telegram-bot',
    long_description=readme(),
    long_description_content_type=readme_type(),
    license='MIT',
    author='Markus Ressel',
    author_email='mail@markusressel.de',
    url='https://github.com/markusressel/telegram-click',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        DEVELOPMENT_STATUS,
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    install_requires=locked_requirements('default'),
    tests_require=locked_requirements('develop'),
)
