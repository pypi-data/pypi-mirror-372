# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/utils/HandleQuotes.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   HandleQuotes.py : Quote handler Base Class
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
from pathlib import Path
import html
import json
from datetime import datetime, timezone
from base64 import b64encode, b64decode

class HandleQuotes:

	def __init__(self):
		""" constructor default"""
		pass

	def _NumStr(self, data):
		""" get num str"""
		return data if data.strip() else '0'

	def _SanitHtml(self, data):
		""" html encode fx"""
		return html.escape(str(data), quote=True).replace("\n",'</br>')

	def _SanitQ(self, data):
		""" add quotes fx private"""
		return str(data).replace("'"," ").replace('"',' ')

	def _SanitL(self, data):
		""" add quotes fx private"""
		return str(data).replace('\n','')

	def _SanitJsonQ(self, data):
		""" add single quotes and protect json"""
		return "'" + json.dumps(data).replace("'","\\'") + "'"

	def _SanitTagQ(self, data):
		""" sanit tags to csv fx private"""
		return str(data).replace("'","&#39;").replace("’","&#39;").replace("`","&#39;").replace('"','&#34;').replace("=","&#61;").replace(',','&comma;')
		# return str(data).replace("'","&#39;").replace('"','&#34;').replace("=","&#61;").replace(',','&comma;')

	def _SanitKey(self, data):
		""" convert dash to underscore private"""
		return str(data).strip().replace("'","").replace('"','').replace("-","_").replace(',','_').replace(' ','_').lower()

	def _SanitUser(self, data):
		""" convert dash to underscore private"""
		return str(data).replace("'","").replace('"','').replace(',','_').lower()

	def _SanitExtreme(self, data):
		""" convert non alnum to underscore"""
		return re.sub(r'\W+', '_', str(data)).lower()

	def _AddSingleQ(self, data):
		""" add quotes fx private"""
		return '"' + str(data).strip('"') + '"'

	def _AddQ(self, data):
		""" add quotes fx private"""
		return '"' + str(data).strip('"') + '"'

	def _AddBackQ(self, data):
		""" add back quotes fx private"""
		return '`' + str(data).strip('`') + '`'

	def _AddNoQ(self, data):
		""" add no quotes fx private"""
		return str(data).strip('"')

	def _JoinEachBackQ(self, data):
		""" join array add back quotes to each fx private"""
		return ', '.join( [self._AddBackQ(str(e)) for e in data] ).strip('"')

	def _JoinEachQ(self, data):
		""" join array add quotes to each fx private"""
		return ', '.join( [self._AddQ(str(e)) for e in data] )

	def _JoinNoQ(self, data):
		""" join array fx private"""
		return ', '.join( [str(e) for e in data] ).strip('"')

	def _JoinQ(self, data):
		""" join array add quotes fx private"""
		return '"' + self._JoinNoQ(data) + '"'

	def _JoinUniqueQ(self, data):
		""" join array unique elements add quotes fx private"""
		done=[]
		for e in data:
			e=str(e)
			if not e in done:
				done.append(e)
		return self._JoinQ(done)

	def _ConvertUnderQ(self, data):
		""" convert underscore to space fx private"""
		return data.replace('_',' ')

	def _BoolNoQ(self, data):
		""" add no quotes bool fx private"""
		return 'TRUE' if data else 'FALSE'

	def _GetPath(self, htpath):
		return htpath if htpath.startswith('/') else Path(Path.cwd(),htpath).as_posix()

	def _GetLast(self, word, delim='::'):
		""" get last of"""
		xx = word.rsplit(delim)
		return xx[ len(xx)-1 ] 

	def _GetFirst(self, word, delim='::'):
		""" get first of"""
		return word.rsplit(delim, 1)[0]

	def _SplitWords(self, words, delim=','):
		""" get array of"""
		out = []
		for word in words.rsplit(delim):
			out.append( word.strip() )
		return out

	def _RequiredField(self, data, field):
		""" init handler required and field from data"""
		if field in data and len(str(data[field])) > 0:
			return data[field]
		raise ValueError("Missing Field: " + field)

	def _RequiredObject(self, data, field):
		""" init handler required for object field from data"""
		if field in data and type(data[field]) is dict:
			return data[field]
		raise ValueError("Missing Object Field: " + field)

	def _RequiredArray(self, data, field):
		""" init handler required for array field from data"""
		if field in data and type(data[field]) is list:
			return data[field]
		raise ValueError("Missing Array Field: " + field)

	def _RequiredInteger(self, data, field):
		""" init handler required int field from data"""
		if field in data:
			return int(data[field])
		raise ValueError("Missing Int Field: " + field)

	def _RequiredFloat(self, data, field):
		""" init handler required float field from data"""
		if field in data:
			return float(data[field])
		raise ValueError("Missing Float Field: " + field)

	def _OptionalField(self, data, field , default=''):
		""" init handler optional and field from data"""
		if field in data and len(str(data[field])) > 0:
			return data[field]
		return default

	def _OptionalMappedField(self, data, field , use_map, default=''):
		""" init handler optional and field from data and map"""
		if field in data and len(str(data[field])) > 0:
			if data[field] in use_map.keys():
				return use_map[ data[field] ]
		return default

	def _OptionalInteger(self, data, field , default=0):
		""" init handler optional int field from data"""
		if field in data:
			return int(data[field])
		return default

	def _OptionalFloat(self, data, field , default=0.0):
		""" init handler optional float field from data"""
		if field in data:
			return float(data[field])
		return default

	def _OptionalBool(self, data, field , default=False):
		""" init handler optional bool field from data"""
		if field in data:
			return bool(data[field])
		return default

	def _OptionalBoolInt(self, data, field , default=0):
		""" init handler optional bool field from data"""
		if field in data:
			return 1 if bool(data[field]) else 0
		return default

	def _YesNoBool(self, data, field, default=False):
		""" init handler yes no bool field from data"""
		if field in data:
			if data[field] in ['YES', 'Yes', 'yes', 'Y', 'y']:
				return True
			elif data[field] in ['NO', 'No', 'no', 'N', 'n']:
				return False
		return default

	def _OptionalObject(self, data, field, default={}):
		""" init handler for object field from data"""
		if field in data and type(data[field]) is dict:
			return data[field]
		return default

	def _OptionalArray(self, data, field, default=[]):
		""" init handler for array field from data"""
		if field in data and type(data[field]) is list:
			return data[field]
		return default

	def _CheckDirExists(self, dname):
		""" check and return the dir path """
		if not os.path.isdir(dname):
			raise ValueError("Not a directory: " + dname)
		return dname

	def _CheckFileExists(self, dname, fname):
		""" check and return the file path """
		path = '/'.join([dname,fname])
		if not os.path.isfile(path):
			raise ValueError("Not a file: " + path)
		return path

	def _MicroS3Path(self):
		""" creates s3 path """
		dt = datetime.now(timezone.utc)
		return "{:08d}/{:06d}/{:06d}".format(
			dt.year * 10000 + dt.month  * 100 + dt.day,
			dt.hour * 10000 + dt.minute * 100 + dt.second,
			dt.microsecond)

	def _MicroFileName(self):
		""" creates filename """
		dt = datetime.now(timezone.utc)
		return "{:08d}_{:06d}_{:06d}".format(
			dt.year * 10000 + dt.month  * 100 + dt.day,
			dt.hour * 10000 + dt.minute * 100 + dt.second,
			dt.microsecond)

	def _JsonToBase64(self, data):
		""" convert json to base 64"""
		return b64encode(json.dumps(data).encode('utf-8')).decode('latin-1')

	def _Base64ToJson(self, data):
		""" convert object base 64 to json """
		return json.loads( b64decode(data) )

