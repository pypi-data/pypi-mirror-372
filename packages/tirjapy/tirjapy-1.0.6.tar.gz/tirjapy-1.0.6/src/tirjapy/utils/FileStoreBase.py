# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/utils/FileStoreBase.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   FileStoreBase.py :  File Store Base
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
import math
import time
from enum import Enum, IntEnum
from tirjapy.utils.TypedEnum import TypedEnum

from tirjapy.utils.HandleQuotes import HandleQuotes
from tirjapy.base.StoreBase import StoreBase
from tirjapy.utils.StorageHandle import StorageHandle
from tirjapy.utils.CalyrexHandle import CalyrexHandle

class SyncTypes(metaclass=TypedEnum):
	LOCAL                       = 'local'             # Local only
	FETCHED                     = 'fetched'           # Fetched from S3
	WRITTEN                     = 'written'           # Written to S3

class ModelPath(HandleQuotes):
	"""Default model path class """

	def __init__(self , xdata):
		""" init fx inits handles """
		self.upload_folder  = self._RequiredField(xdata, 'upload_folder')
		self.s3_bucket      = self._RequiredField(xdata, 's3_bucket')
		self.work_path      = self._MicroS3Path()

	def GetData(self, blank=False):
		""" Prints Json of class """
		return {
			's3_bucket'  : self.s3_bucket,
			'work_path' : self.work_path,
			'upload_folder' : self.upload_folder,
		}

class FileStoreBase(StoreBase):

	def __init__(self):
		""" default constructor """

		# - File File Tags
		self.s3_bucket            = ''                  # String.       S3 Bucket 
		self.s3_path              = ''                  # String.       S3 Path for file
		self.local_path           = ''                  # String.       Local Path for file

		self.clean                = False               # Bool.         If set file is cleaned, default False
		self.fetched              = False               # Bool.         If set file is fetched
		self.sync_type            = SyncTypes.LOCAL     # Enum.         Sync State for file

	# Functions

	def GetData(self, blank=False):
		""" getter for json """
		if blank and len(self.s3_bucket)==0 and len(self.s3_path)==0 and len(self.local_path)==0:
			return {}
		return {
			's3_bucket' : self.s3_bucket,
			's3_path' : self.s3_path,
			'local_path' : self.local_path,
			'sync_type' : self.sync_type
		}

	def InitData(self, data, file_name):
		""" init for using MakePptxStore and file_name"""
		self.s3_bucket = data.s3_bucket
		self.s3_path = '/'.join([data.work_path, file_name])
		self.local_path = '/'.join([data.upload_folder, self.s3_bucket, self.s3_path])
		dirname = os.path.dirname(self.local_path)
		os.makedirs(dirname,exist_ok = True)

	def WriteLocal(self, file_obj, overwrite=False):
		""" Writes to local, overwrite"""
		if not overwrite and os.path.exists(self.local_path):
			raise ValueError(f"File exists at {self.local_path}")
		dirname = os.path.dirname(self.local_path)
		os.makedirs(dirname,exist_ok = True)
		file_obj.seek(0)
		file_obj.save(self.local_path)

	def WriteToS3(self, overwrite=False):
		""" Writes to S3"""
		if self.fetched and (not overwrite):
			return None
		shandle = StorageHandle()
		shandle.WriteFileObj(self)
		self.sync_type=SyncTypes.WRITTEN
		self.fetched=True
		
	def _FetchFromS3(self , overwrite=False):
		""" Reads from S3"""
		if (not overwrite) and os.path.isfile(self.local_path):
			return None
		dirname = os.path.dirname(self.local_path)
		os.makedirs(dirname,exist_ok = True)
		shandle = StorageHandle()
		shandle.ReadFileObj(self)
		self.sync_type=SyncTypes.FETCHED
		self.fetched=True

	def GetLocalPath(self):
		""" Get Local file path """
		if len(self.local_path)==0:
			raise ValueError("local_path is blank")
		return self.local_path

	def LocalRequired(self , overwrite=False):
		""" Get Local file, if not fetch from S3 Reads from S3"""
		self._FetchFromS3(overwrite)
		return self.local_path

	def LocalOptional(self , overwrite=False):
		""" Ignore blank, Get Local file, if not fetch from S3 Reads from S3"""
		if len(self.local_path)>0:
			return self.LocalRequired(overwrite)
		return ''

	def GetCalyrexURL(self, user=''):
		""" Gets Calyrex URL"""
		chandle = CalyrexHandle()
		return chandle.GetURL( user, self.s3_bucket, self.s3_path)
		
	def CleanUp(self):
		""" Deletes local file"""
		if self.local_path and self.clean:
			self._CleanUpFile( self._GetPath(self.local_path))

