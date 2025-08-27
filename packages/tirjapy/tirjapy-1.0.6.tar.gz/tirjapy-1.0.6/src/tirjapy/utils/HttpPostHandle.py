# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/utils/HttpPostHandle.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   HttpPostHandle.py : HttpPost Handler
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
import re
import json
import urllib3
from base64 import b64encode

from tirjapy.utils.HandleQuotes import HandleQuotes
from tirjapy.base.HandleConstants import \
	HTTP_CONNECT_TIMEOUT, HTTP_READ_TIMEOUT, LONG_CONNECT_TIMEOUT, LONG_READ_TIMEOUT

class HttpPostHandle(HandleQuotes):

	my_http_pool_manager = None

	def __init__(self):
		""" constructor default"""
		self._Initialize()
		self.http = HttpPostHandle.my_http_pool_manager

	def _Initialize(self):
		""" Init fx"""
		if HttpPostHandle.my_http_pool_manager:
			return None
		timeout = urllib3.util.Timeout(connect=LONG_CONNECT_TIMEOUT, read=LONG_READ_TIMEOUT)
		pool_manager = urllib3.PoolManager(timeout=timeout)
		HttpPostHandle.my_http_pool_manager = pool_manager

	def _PopulateBasicHeaderCreds(self, headers, username, passwd):
		""" function to load username password in headers """
		if len(username)>0 and len(passwd)>0:
			use_creds = ':'.join([username,passwd])
			base64creds = b64encode(use_creds.encode('ascii'))
			headers['Authorization'] = "Basic {}".format(base64creds.decode('ascii'))

	def PostFile(self, filename, url, username, passwd):
		""" post file as form file """

		if len(url)<6:
			raise ValueError("url icannot be empty")
		## handle headers
		headers = {}
		self._PopulateBasicHeaderCreds( headers, username, passwd )

		output = { 'error' : True , 'status' : 'unknown' }
		with open(filename,'rb') as f:
			file_data = f.read()
			fields={ "file": ( os.path.basename(filename) , file_data) }
			body, content_type = urllib3.filepost.encode_multipart_formdata(fields)
			headers['Content-Type'] = content_type
			
			r = self.http.request( 'POST', url, headers=headers, body=body)
			if r.status==200:
				output = json.loads( r.data.decode('utf-8') )

		return output

	def PostJsonData(self, data, url, username, passwd):
		""" post file as json data """

		if len(url)<6:
			raise ValueError("url cannot be empty")
		## handle headers
		headers = {}
		self._PopulateBasicHeaderCreds( headers, username, passwd )
		headers['Content-Type'] = 'application/json'

		output = { 'error' : True , 'status' : 'unknown' }
		r = self.http.request( 'POST', url, headers=headers, body=json.dumps(data))
		# print(r.status)

		if r.status==200:
			output = json.loads( r.data.decode('utf-8') )
		return output

	def GetJsonData(self, url, username, passwd, fields={}):
		""" get file as json data """

		if len(url)<6:
			raise ValueError("url cannot be empty")
		## handle headers
		headers = {}
		self._PopulateBasicHeaderCreds( headers, username, passwd )
		output = { 'error' : True , 'status' : 'unknown' }

		r = self.http.request( 'GET', url, headers=headers, fields=fields)

		if r.status==200:
			output = json.loads( r.data.decode('utf-8') )
		return output

