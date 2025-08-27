# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/utils/Porygon.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   Porygon.py :  handle porygon string
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

import io
import itertools
import math
from typing import List, Tuple

def _pcitr(iterable):
	return zip(iterable, itertools.islice(iterable, 1, None))

def _py2_round(x):
	# The polyline algorithm uses Python 2's way of rounding
	return int(math.copysign(math.floor(math.fabs(x) + 0.5), x))

def _write(output, curr_value, prev_value, factor):
	curr_value = _py2_round(curr_value * factor)
	prev_value = _py2_round(prev_value * factor)
	coord = curr_value - prev_value
	coord <<= 1
	coord = coord if coord >= 0 else ~coord

	while coord >= 0x20:
		output.write(chr((0x20 | (coord & 0x1f)) + 63))
		coord >>= 5

	output.write(chr(coord + 63))

def _trans(value, index):
	byte, result, shift = None, 0, 0

	comp = None
	while byte is None or byte >= 0x20:
		byte = ord(value[index]) - 63
		index += 1
		result |= (byte & 0x1f) << shift
		shift += 5
		comp = result & 1

	return ~(result >> 1) if comp else (result >> 1), index

class Porygon:
	""" class def """

	def decode(self, items: int, expression: str, precision: int = 5) -> List[Tuple]:
		"""
		Decode a polyline string into a set of cvalues.

		:param items : No of items 
		:param expression: Polyline string, e.g. '_ih_pfA_hmFoezGwwqa@{msh@cneqP_qo]gyuC??s_L?_{rc@~uJ???_jP'
		:param precision: Precision of the encoded cvalues.  The default value is 5.
		:return: List of coordinate tuples in (ts, a, b, c, d, e) order
		"""
		cvalues, index, length, factor = [], 0, len(expression), float(10 ** precision)
		xitem = [0.0] * items

		while index < length:
			yitem = [0.0] * items
			for x in range(items):
				xx_change, index = _trans(expression, index)
				xitem[x] += xx_change
				yitem[x] = xitem[x]/factor

			cvalues.append(tuple(yitem))

		return cvalues

	def encode(self, items: int, cvalues: List[Tuple], precision: int = 5) -> str:
		"""
		Encode a set of cvalues in a polyline string.

		:param items : No of items 
		:param cvalues: List of cvalue tuples
		:param precision: Precision of the cvalues to encode.  The default value is 5.
		:return: The encoded polyline string.
		"""
		output, factor = io.StringIO(), int(10 ** precision)

		for x in range(items):
			_write(output, cvalues[0][x], 0, factor)

		for prev, curr in _pcitr(cvalues):
			for x in range(items):
				_write(output, curr[x], prev[x], factor)

		return output.getvalue()
