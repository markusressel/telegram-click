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
import operator
from abc import abstractmethod
from functools import reduce

from telegram import Update
from telegram.ext import CallbackContext


class Permission:

    def __call__(self, update: Update, context: CallbackContext, command: str) -> bool:
        return self.evaluate(update, context, command)

    def __and__(self, other):
        return self._merge(other, operator.and_)

    def __or__(self, other):
        return self._merge(other, operator.or_)

    def _merge(self, other, op: operator):
        if isinstance(self, MergedPermission):
            merged = self
            to_merge = other
        elif isinstance(other, MergedPermission):
            merged = other
            to_merge = self
        else:
            merged = None
            to_merge = None

        if merged is not None and merged.op == op:
            if isinstance(to_merge, MergedPermission):
                merged.permissions.update(to_merge.permissions)
            else:
                merged.permissions.add(to_merge)
            return merged

        return MergedPermission({self, other}, op)

    def __invert__(self):
        return InvertedPermission(self)

    @abstractmethod
    def evaluate(self, update: Update, context: CallbackContext, command: str) -> bool:
        """
        Evaluates if the permission should be granted
        :param update: the message update
        :param context: the message context
        :param command: the executed command
        :return: True if the permission is granted, False otherwise
        """
        raise NotImplementedError()


class InvertedPermission(Permission):
    """
    Represents a permission that has been inverted.
    """

    def __init__(self, original_permission: Permission):
        """
        :param original_permission: the non-inverted permission
        """
        self.original_permission = original_permission

    def evaluate(self, update: Update, context: CallbackContext, command: str) -> bool:
        return not bool(self.original_permission(update, context, command))


class MergedPermission(Permission):
    """
    Represents a permission consisting of two other permissions.
    """

    def __init__(self, permissions: set, op: operator):
        """

        :param permissions: Permission objects to merge
        :param op: operation to use
        """
        self.permissions = permissions
        self.op = op

        if self.op not in [operator.and_, operator.or_]:
            raise ValueError("Only operator.and_, operator.or_ are supported")

    def evaluate(self, update: Update, context: CallbackContext, command: str):
        """
        Evaluates all given permissions and combines their result using the given operator
        :return: reduced evaluation result
        """
        evaluations = list(map(lambda x: x.evaluate(update, context, command), self.permissions))
        return reduce(lambda x, y: self.op(x, y), evaluations)
