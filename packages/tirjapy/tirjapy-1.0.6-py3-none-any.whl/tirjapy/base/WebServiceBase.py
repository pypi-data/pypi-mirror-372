# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/base/WebServiceBase.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   WebServiceBase.py : base for Web Service
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
import random
import uuid
import base64
import string
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class WebServiceBase():
	"""Default Simple WebService base class."""

	def _GetPath(self, htpath):
		return htpath if htpath.startswith('/') else Path(Path.cwd(),htpath).as_posix()

	def _RequiredField(self, data, field, blank_ok=False):
		""" init handler required and field from data"""
		if field in data and len(str(data[field])) > 0:
			return data[field]
		elif field in data and blank_ok:
			return data[field]
		raise ValueError("Missing Field: " + field)

	def _RequiredInteger(self, data, field, blank_ok=True):
		""" init handler required int field from data"""
		if field in data and len(str(data[field])) > 0:
			return int(data[field])
		elif field in data and blank_ok:
			return 0
		raise ValueError("Missing Integer: " + field)

	def _RequiredFloat(self, data, field, blank_ok=True):
		""" init handler required float field from data"""
		if field in data and len(str(data[field])) > 0:
			return float(data[field])
		elif field in data and blank_ok:
			return 0.0
		raise ValueError("Missing Float: " + field)

	def _RequiredArray(self, data, field):
		""" init handler required for array field from data"""
		if field in data and type(data[field]) is list:
			return data[field]
		raise ValueError("Missing Array Field: " + field)

	def _OptionalField(self, data, field , default=''):
		""" init handler optional and field from data"""
		if field in data and len(str(data[field])) > 0:
			return data[field]
		return default

	def _OptionalInteger(self, data, field , default=0):
		""" init handler optional int field from data"""
		if field in data and len(str(data[field])) > 0:
			return int(data[field]) 
		return default

	def _OptionalFloat(self, data, field , default=0.0):
		""" init handler optional float field from data"""
		if field in data and len(str(data[field])) > 0:
			return float(data[field])
		return default

	def _OptionalArray(self, data, field, default=[]):
		""" init handler for array field from data"""
		if field in data and type(data[field]) is list:
			return data[field]
		return default

	def _HandlePost(self, request):
		""" get post content"""
		content_type = request.headers.get('Content-Type')
		if content_type == 'application/json':
			return request.json
		elif re.match('multipart/form-data',content_type) or re.match('application/x-www-form-urlencoded',content_type):
			robj = {}
			for item in request.form.keys():
				robj[item]=request.form[item]
			return robj
		else:
			return {}

	def _EncodeDict(self, skey, data):
		usekey=base64.b64decode(skey)
		BS=AES.block_size
		iv = ''.join(random.choices(string.ascii_lowercase + string.digits, k = BS))
		# aes = AES.new(key, AES.MODE_CBC, bytes(iv,'utf8'))
		aes = AES.new(usekey, AES.MODE_CBC, iv.encode('utf8'))
		xdata = json.dumps(data)
		pad = BS - len(xdata) % BS
		xdata = xdata + pad * chr(pad)
		encrypted = aes.encrypt(xdata.encode('utf8'))
		return iv+base64.urlsafe_b64encode(encrypted).decode('utf8')

	def _DecodeDict(self, skey, data):
		output = ""
		try:
			usekey=base64.b64decode(skey)
			BS=AES.block_size
			iv = data[:BS]
			cipher = AES.new(usekey, AES.MODE_CBC, iv.encode('utf8') )
			output = unpad(cipher.decrypt( base64.urlsafe_b64decode(data[BS:]) ), BS).decode('utf-8')
		except:
			output = "{}"

		return json.loads(output)

	def _PopulateBasicHeaderCreds(self, headers, username, passwd):
		""" function to populate username password in headers """

		if not username or not passwd:
			return headers
		use_creds = ':'.join([username,passwd])
		base64creds = base64.b64encode(use_creds.encode('ascii'))
		headers['Authorization'] = "Basic {}".format(base64creds.decode('ascii'))

	def _SplitCredsFx(self, creds):
		""" function to server, username, passwd from creds for backward compat """
		server = self._RequiredField( creds, 'server' )
		username = self._OptionalField( creds, 'username' )
		passwd = self._OptionalField( creds, 'passwd' )
		return ( server , username, passwd )

	def _PostJsonData(self, creds, uri, data):
		""" post file as json data """

		## pre-flight
		server, username, passwd = self._SplitCredsFx(creds)
		url = '/'.join([server, uri])

		## handle headers
		headers = {}
		self._PopulateBasicHeaderCreds(headers, username, passwd)
		headers['Content-Type'] = 'application/json'

		output = { 'error' : True , 'status' : 'unknown' }
		r = self.http.request( 'POST', url, headers=headers, body=json.dumps(data))
		# print(r.status)

		if r.status==200:
			output = json.loads( r.data.decode('utf-8') )
		return output

	def _PostFormData(self, creds, uri, fields):
		""" post file as json data """

		## pre-flight
		server, username, passwd = self._SplitCredsFx(creds)
		url = '/'.join([server, uri])

		## handle headers
		headers = {}
		self._PopulateBasicHeaderCreds(headers, username, passwd)

		output = { 'error' : True , 'status' : 'unknown' }
		r = self.http.request( 'POST', url, headers=headers, fields=fields, encode_multipart=True)

		if r.status==200:
			output = json.loads( r.data.decode('utf-8') )
		return output

	def _GetJsonData(self, creds, uri, fields={}):
		""" get file as json data """

		## pre-flight
		server, username, passwd = self._SplitCredsFx(creds)
		url = '/'.join([server, uri])

		## handle headers
		headers = {}
		self._PopulateBasicHeaderCreds(headers, username, passwd)
		output = { 'error' : True , 'status' : 'unknown' }
		r = self.http.request( 'GET', url, headers=headers, fields=fields)

		if r.status==200:
			output = json.loads( r.data.decode('utf-8') )
		return output

