"""
 * Copyright (c) 2008 Zivios, LLC.
 *
 * This file is part of Zivios.
 *
 * Zivios is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Zivios is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Zivios.  If not, see <http://www.gnu.org/licenses/>.
 *
 * @package		ZiviosAgent
 * @copyright	Copyright (c) 2008 Zivios, LLC. (http://www.zivios.org)
 * @license		http://www.zivios.org/legal/license
 * @version		$Id: Exception.php 908 2008-08-25 11:03:00Z fkhan $
 * @subpackage  Core
"""

from twisted.web import xmlrpc
import logging
import os
import popen2
import re
import string
import time
import datetime
from twisted.python import log
import ZiviosAgent

class ntp(ZiviosAgent.ZiviosAgent):
                
    def xmlrpc_addService(self):
        print 'ntp addService function called'

    def xmlrpc_serviceStatus(self):
        response,regexcode,exitcode = self.command("statusntpcommand")
        return (exitcode==0)
    
    def xmlrpc_stopService(self):
        response,regexcode,exitcode = self.command("stopntpcommand")
        return (exitcode==0)
    
    def xmlrpc_startService(self):
        response,regexcode,exitcode = self.command("startntpcommand")
        return (exitcode==0)
        
    def xmlrpc_currentTime(self):
        now = datetime.datetime.now()
        return now.ctime()
        
    def xmlrpc_getTimezone(self):
        tz,tzm = time.tzname
        return tzm;

    def xmlrpc_getsyncstatus(self):
        #sanitizing output!
        response,regexcode,exitcode = self.command("ntpq");
        resp = response.split('\n')
        if (len(resp) <= 2):
            return -1
            
        del resp[0:2]
        length = len(resp)
        del resp[length-1]
        retarray = []
        for a in resp:
            a = a.lstrip()
            a = a.rstrip()
            joinarray = re.split('\s+',a)
            retarray.append(joinarray)
        return retarray
    
    
    def xmlrpc_getGmtOffset(self):
        return time.timezone/3600;
