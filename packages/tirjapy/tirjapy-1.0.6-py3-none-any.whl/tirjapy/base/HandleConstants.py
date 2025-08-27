# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/base/HandleConstants.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   HandleConstants.py : Handle different timeouts and constants
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

## symbols
COMMA = ','
SPACE = ' '
EQUALTO = '='
NOTEQUALTO = '!='
BLANK = ''
COLON = ':'

# http post

HTTP_CONNECT_TIMEOUT     =     60                 # default http connect timeout
HTTP_READ_TIMEOUT        =    300                 # default http read timeout

LONG_CONNECT_TIMEOUT     =    600                 # long http connect timeout
LONG_READ_TIMEOUT        =    600                 # long http read timeout

# redis

TASK_CANCEL_HSET         = 'nb_def_cancel'        # task cancel hset
TASK_DO_CANCEL           = b'cancel'              # task cancel val

