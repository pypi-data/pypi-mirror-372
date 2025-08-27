# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/base/StoreBase.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   StoreBase.py : Storage Baisc Data Model
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

import os
import json
from datetime import datetime
import hashlib
from enum import Enum, IntEnum
from tirjapy.utils.TypedEnum import TypedEnum

from tirjapy.utils.HandleQuotes import HandleQuotes

class TaskState(metaclass=TypedEnum):
	NONE                        = ''
	QUEUED                      = 'queued'
	ONGOING                     = 'ongoing'
	DONE                        = 'done'
	FAILED                      = 'failed'
	ACCEPTED                    = 'accepted'
	NOTFOUND                    = 'notfound'
	CANCELLED                   = 'cancelled'

class StoreBase(HandleQuotes):

	def __init__(self):
		""" init fx inits handles """
		pass

	def _SaveLocalFile(self, xfile, savepath):
		""" Writes to disk with recursive mkdir"""
		dirname = os.path.dirname(savepath)
		if not os.path.exists(dirname):
				os.makedirs(dirname,exist_ok = True)
		xfile.save( savepath )

	def _CleanUpFile(self, fname):
		""" recursively clean file """
		## delete files
		dname = fname
		try:
			os.remove(dname)
			dname = os.path.dirname(dname)
			while len(dname) > 1:
				os.rmdir(dname)
				dname = os.path.dirname(dname)
		except:
			pass
		print("Cleanup: Till : %s" % dname , flush=True)

	def GetData(self, blank=False):
		""" TO INHERIT: Prints Json of class """
		raise ValueError("GetData not implemented in StoreBase")

	def _GetHashOne(self, one):
		return hashlib.sha256(one.encode()).hexdigest()

	def _GetHashTwo(self, one, two):
		return hashlib.sha256('|'.join([one,two]).encode()).hexdigest()

