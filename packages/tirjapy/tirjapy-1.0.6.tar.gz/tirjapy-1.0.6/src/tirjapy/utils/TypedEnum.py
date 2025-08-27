# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/utils/TypedEnum.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   TypedEnum.py : type preserving enumeration metaclass.
# 
# @section LICENSE
# 
# Copyright (c) 2025 Shreos Roychowdhury.
# Copyright (c) 2025 Tirja Consulting LLP.
# 
# This source code is protected under international copyright law.  All rights
# reserved and protected by the copyright holders.
#
# This file is confidential and only available to authorized individuals with the
# permission of the copyright holders.  If you encounter this file and do not have
# permission, please contact the copyright holders and delete this file.
#
# THE SOFTWARE IS PROVIDED , WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

class TypedEnum(type):
	"""This metaclass creates an enumeration that preserves isinstance(element, type)."""

	def __new__(mcs, cls, bases, classdict):
		"""Discover the enum members by removing all intrinsics and specials."""
		object_attrs = set(dir(type(cls, (object,), {})))
		member_names = set(classdict.keys()) - object_attrs
		member_names = member_names - set(name for name in member_names if name.startswith("_") and name.endswith("_"))
		new_class = None
		base = None
		for attr in member_names:
			value = classdict[attr]
			if new_class is None:
				# base class for all members is the type of the value
				base = type(classdict[attr])
				ext_bases = (*bases, base)
				new_class = super().__new__(mcs, cls, ext_bases, classdict)
				setattr(new_class, "__member_names__", member_names)
			else:
				if not base == type(classdict[attr]):  # noqa
					raise SyntaxError("Cannot mix types in TypedEnum")
			new_val = new_class.__new__(new_class, value)
			setattr(new_class, attr, new_val)

		for parent in bases:
			new_names = getattr(parent, "__member_names__", set())
			member_names |= new_names
			for attr in new_names:
				value = getattr(parent, attr)
				if not isinstance(value, base):
					raise SyntaxError("Cannot mix inherited types in TypedEnum: %s from %s" % (attr, parent))
				# convert all inherited values to the new class
				setattr(new_class, attr, new_class(value))

		return new_class

	def __call__(cls, arg):
		for name in cls.__member_names__:
			if arg == getattr(cls, name):
				return type.__call__(cls, arg)
		raise ValueError("Invalid value '%s' for %s" % (arg, cls.__name__))

	@property
	def __members__(cls):
		"""Sufficient to make the @unique decorator work."""

		class FakeEnum:  # pylint: disable=too-few-public-methods
			"""Object that looks a bit like an Enum instance."""

			def __init__(self, name, value):
				self.name = name
				self.value = value

		return {name: FakeEnum(name, getattr(cls, name)) for name in cls.__member_names__}

	def __iter__(cls):
		"""List all enum values."""
		return (getattr(cls, name) for name in cls.__member_names__)

	def __len__(cls):
		"""Get number of enum values."""
		return len(cls.__member_names__)

