# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/utils/StorageHandle.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   StorageHandle.py : AWS S3 handlers
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
import sys
import json
import boto3
from boto3.s3.transfer import S3Transfer
import mimetypes

from tirjapy.utils.HandleQuotes import HandleQuotes

MIME_UNKNOWN = 'application/octet-stream'

class StorageHandle(HandleQuotes):

	s3_creds = None

	def __init__(self):
		""" constructor default"""
		self.is_init = False
		if StorageHandle.s3_creds:
			self._Initialize()

	def _SanityCheck(self):
		""" check if globals set """
		if not self.is_init:
			raise ValueError("S3 Credentials not set in StorageHandle")

	def _ValidateDataObj(self, data):
		""" check if data is ok """
		if not data.s3_bucket:
			raise ValueError("s3_bucket not set")
		if not data.s3_path:
			raise ValueError("s3_path not set")
		if not data.local_path:
			raise ValueError("local_path not set")

	def RegisterGlobals(self, params):
		"""Register Global fx"""

		StorageHandle.s3_creds = {
			'access_key' : self._RequiredField( params , 'access_key' ),
			'secret_key' : self._RequiredField( params , 'secret_key' ),
			'bucket' : self._RequiredField( params , 'bucket' ),
			'region' : self._RequiredField( params , 'region' ),
			'bucket2' : self._OptionalField( params , 'bucket2' ),
			'region2' : self._OptionalField( params , 'region2' ),
			'format' : self._OptionalField( params , 'format' , 'json'),
		}
		self._Initialize()

	def _Initialize(self):
		""" Init fx"""
		self.bucket = StorageHandle.s3_creds['bucket']
		self.client = boto3.client('s3', StorageHandle.s3_creds['region'],
			aws_access_key_id=StorageHandle.s3_creds['access_key'],
			aws_secret_access_key=StorageHandle.s3_creds['secret_key']
		)
		self.transfer = S3Transfer( self.client )

		## set a second bucket if valid
		self.has_two_buckets = False
		if ( StorageHandle.s3_creds['bucket2'] and StorageHandle.s3_creds['region2'] ):
			self.has_two_buckets = True
			self.bucket2 = StorageHandle.s3_creds['bucket2']
			self.transfer2 = S3Transfer(
				boto3.client('s3', StorageHandle.s3_creds['region2'],
					aws_access_key_id=StorageHandle.s3_creds['access_key'],
					aws_secret_access_key=StorageHandle.s3_creds['secret_key']
				)
			)
			print("S3 Storage : configured two bucket", flush=True)
		## is init
		self.is_init = True

	def _GetMimeType(self, filename):
		""" Gets the mime type """
		mime, encd = mimetypes.guess_type(filename)
		return MIME_UNKNOWN if not mime else mime

	def GetBucket(self):
		""" Gets the bucket """
		if 'bucket' not in self.__dict__:
			print("S3 bucket lookup : FAILED", flush=True)
			raise ValueError("Bucket not set yet")
		return self.bucket

	def WriteFile(self, loc, rem, mime_type):
		""" Writes file to S3 both bucket and if present bucket2"""
		self._SanityCheck()
		extra_args={'ContentType' : mime_type}
		self.transfer.upload_file(loc, self.bucket, rem, extra_args=extra_args)
		if self.has_two_buckets:
			self.transfer2.upload_file(loc, self.bucket2, rem, extra_args=extra_args)

	def ReadFile(self, bucket, s3path, savepath):
		""" Reads file from S3 from bucket only"""
		self._SanityCheck()
		dirname = os.path.dirname(savepath)
		if not os.path.exists(dirname):
				os.makedirs(dirname,exist_ok = True)
		self.transfer.download_file(bucket, s3path, savepath)

	def WriteFileObj(self, data):
		""" Writes file to S3 using FileStore Object as data"""
		self._SanityCheck()
		self._ValidateDataObj(data)
		## take mime type from extn
		mime_type = self._GetMimeType( data.s3_path )
		extra_args={'ContentType' : mime_type}
		## copy
		self.transfer.upload_file(data.local_path, data.s3_bucket, data.s3_path, extra_args=extra_args)

	def ReadFileObj(self, data):
		""" Reads file from S3 using FileStore Object as data"""
		self._SanityCheck()
		self._ValidateDataObj(data)
		## copy
		self.transfer.download_file(data.s3_bucket, data.s3_path, data.local_path)

