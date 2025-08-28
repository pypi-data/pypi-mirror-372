# -*- coding: utf-8 -*-

# Mathmaker creates automatically maths exercises sheets
# with their answers
# Copyright 2006-2017 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Mathmaker.

# Mathmaker is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# Mathmaker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Mathmaker; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from abc import ABCMeta, abstractmethod


# ------------------------------------------------------------------------------
# --------------------------------------------------------------------------
# ------------------------------------------------------------------------------
##
# @class Clonable
# @brief All objects that are used must be able to be copied deeply
# Any Clonable are provided the clone() method, no need to reimplement it
class Clonable(object):

    # --------------------------------------------------------------------------
    ##
    #   @brief Returns a deep copy of the object
    def clone(self):
        result = object.__new__(type(self))
        result.__init__(self)
        return result


# ------------------------------------------------------------------------------
# --------------------------------------------------------------------------
# ------------------------------------------------------------------------------
##
# @class NamedObject
# @brief Abstract mother class of objects having a name
class NamedObject(Clonable, metaclass=ABCMeta):

    # --------------------------------------------------------------------------
    ##
    #   @brief Constructor
    #   @warning Must be redefined
    @abstractmethod
    def __init__(self):
        pass

    # --------------------------------------------------------------------------
    ##
    #   @brief Returns the name of the object
    @property
    def name(self):
        return self._name

    # --------------------------------------------------------------------------
    ##
    #   @brief Sets the name of the object
    @name.setter
    def name(self, arg):
        if not (type(arg) == str or type(arg) == int):
            raise ValueError('Got: ' + str(type(arg)) + 'instead of str|int')

        self._name = str(arg)


# ------------------------------------------------------------------------------
# --------------------------------------------------------------------------
# ------------------------------------------------------------------------------
##
# @class Printable
# @brief All Printable objects: Exponenteds & others (Equations...)
# Any Printable must reimplement the into_str() method
class Printable(NamedObject, metaclass=ABCMeta):

    # --------------------------------------------------------------------------
    ##
    #   @brief Creates a string of the given object in the given ML
    #   @param options Any options
    #   @return The formated string
    @abstractmethod
    def into_str(self, **options):
        pass

    @property
    def printed(self):
        """
        Shortcut for self.into_str(force_expression_begins=True)

        This returns the string of the Printable object, assuming it starts
        the expression.
        """
        return self.into_str(force_expression_begins=True)

    @property
    def jsprinted(self):
        """
        Shortcut for self.into_str(force_expression_begins=True, js_repr=True)

        This returns the string of the Printable object, assuming it starts
        the expression.
        """
        return self.into_str(force_expression_begins=True, js_repr=True)
