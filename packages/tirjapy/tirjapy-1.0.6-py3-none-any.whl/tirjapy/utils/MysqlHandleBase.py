# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/utils/MysqlHandleBase.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   MysqlHandleBase.py :  Mysql handle Base Fx
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

import mysql.connector
from mysql.connector import errorcode

from tirjapy.utils.HandleQuotes import HandleQuotes

class MysqlHandleBase(HandleQuotes):
	""" mysql handled class """

	my_creds = None

	def __init__(self):
		""" constructor default"""
		self.is_init = False
		if MysqlHandleBase.my_creds:
			self._InitMysql()

	def __del__(self):
		""" destructor default"""
		if self.is_init:
			## handle "ImportError: No localization support for language 'eng'"
			try:
				self.session.close()
			except:
				pass

	def _InitMysql(self):
		if self.is_init:
			return
		self.session = mysql.connector.connect(
    	host= MysqlHandleBase.my_creds['host'], port= MysqlHandleBase.my_creds['port'],
			user= MysqlHandleBase.my_creds['user'], password= MysqlHandleBase.my_creds['pass'],
			autocommit=True)
		self.db_main = MysqlHandleBase.my_creds['db_main']
		self.is_init = True

	def RegisterGlobals(self, params):
		"""Register Global fx"""

		MysqlHandleBase.my_creds = {
			'host' : self._RequiredField(params, 'host'),
			'port' : self._RequiredField(params, 'port'),
			'user' : self._RequiredField(params, 'user'),
			'pass' : self._RequiredField(params, 'pass'),
			'db_main' : self._RequiredField(params, 'db_main'),
		}
		self._InitMysql()

	def _CheckInit(self):
		if not self.is_init:
			raise ValueError("Mysql Vars not found")

	def _MysqlUpdate(self, db, sql, multi=False):
		""" Internal Mysql Update Handler"""
		session = self.session
		session.database = db
		cursor = session.cursor()

		noerr = False

		try:
			#cursor.execute(sql,multi=multi) ## depre in 9
			cursor.execute(sql)
			noerr = True

		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
				print("table already exists.", flush=True)
			else:
				print(err.msg, flush=True)

		cursor.close()
		return noerr

	def _MysqlUpdateTuple(self, db, sql, tvals):
		""" Internal Mysql Update Handler"""
		session = self.session
		session.database = db
		cursor = session.cursor()

		noerr = False
		try:
			cursor.execute(sql,tvals)
			noerr = True
		except mysql.connector.Error as err:
			print(err.msg, flush=True)

		cursor.close()
		return noerr

	def _MysqlSelect(self, db, sql):
		""" Internal Mysql Select Handler"""

		session = self.session
		session.database = db
		cursor = session.cursor()
		data = []
		try:
			cursor.execute(sql)
			while True:
				rows = cursor.fetchmany(1000)
				if not rows:
					break
				data.extend(rows)
		except mysql.connector.Error as err:
			print(err.msg, flush=True)

		cursor.close()
		return data

	def _MysqlSelectToWriter(self, db, sql, tsv_writer):
		""" Internal Mysql Select Handler to tsv_writer"""

		session = self.session
		session.database = db
		cursor = session.cursor()
		try:
			cursor.execute(sql)
			while True:
				rows = cursor.fetchmany(1000)
				if not rows:
					break
				tsv_writer.writerows(rows)
		except mysql.connector.Error as err:
			print(err.msg, flush=True)

		cursor.close()

	def _MysqlGetLastInsert(self, db, sql):
		""" Mysql Fx to get last id """

		toret = 0
		session = self.session
		session.database = db
		cursor = session.cursor()
		try:
			cursor.execute(sql)
			toret = int(cursor.lastrowid)
		except mysql.connector.Error as err:
			print(err.msg, flush=True)

		cursor.close()
		return toret
