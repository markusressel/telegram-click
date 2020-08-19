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

import operator
from abc import abstractmethod
from functools import reduce
from typing import Dict

from telegram import Update
from telegram.ext import CallbackContext


class Permission:

    def __call__(self, update: Update, context: CallbackContext) -> bool:
        return self.evaluate(update, context)

    def __and__(self, other):
        return self._merge(other, operator.and_)

    def __or__(self, other):
        return self._merge(other, operator.or_)

    def _merge(self, other, op: operator):
        return MergedPermission([self, other], op)

    def __invert__(self):
        return InvertedPermission(self)

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    @abstractmethod
    def evaluate(self, update: Update, context: CallbackContext) -> bool:
        """
        Evaluates if the permission should be granted
        :param update: the message update
        :param context: the message context
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

    def evaluate(self, update: Update, context: CallbackContext) -> bool:
        return not bool(self.original_permission(update, context))

    def __str__(self):
        return "(not {})".format(self.original_permission.__str__())

    def __repr__(self):
        return "<not {}>".format(self.original_permission.__repr__())


class MergedPermission(Permission):
    """
    Represents a permission consisting of two other permissions.
    """

    def __init__(self, permissions: list, op: operator):
        """

        :param permissions: Permission objects to merge
        :param op: operation to use
        """
        self.permissions = permissions
        self.op = op

        if self.op not in [operator.and_, operator.or_]:
            raise ValueError("Only operator.and_, operator.or_ are supported")

    def evaluate(self, update: Update, context: CallbackContext) -> bool:
        """
        Evaluates all given permissions and combines their result using the given operator
        :return: reduced evaluation result
        """
        evaluations = list(map(lambda x: x.evaluate(update, context), self.permissions))
        return reduce(lambda x, y: self.op(x, y), evaluations)

    def __str__(self):
        permission_class_names = list(map(lambda x: x.__str__(), self.permissions))
        string = " {} ".format(self.op.__name__).join(permission_class_names)
        return "({})".format(string)

    def __repr__(self):
        permission_class_names = list(map(lambda x: x.__repr__(), self.permissions))
        repr = " {} ".format(self.op.__name__[1:]).join(permission_class_names)
        return "<{}>".format(repr)


def get_evaluation_tree(update: Update, context: CallbackContext, permission: Permission) -> any:
    def add_child(tree_node: Dict, permission: Permission):
        evaluation = permission.evaluate(update, context)
        tree_node["permission"] = permission
        tree_node["evaluation"] = evaluation

        if isinstance(permission, MergedPermission):
            tree_node["op"] = permission.op
            tree_node["left"] = {}
            add_child(tree_node["left"], permission.permissions[0])
            tree_node["right"] = {}
            add_child(tree_node["right"], permission.permissions[1])

    root = {}
    add_child(root, permission)
    return root
