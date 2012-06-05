"""
 * Copyright (c) 2008-2010 Zivios, LLC.
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
 * @package     ZiviosAgent
 * @copyright   Copyright (c) 2008-2010 Zivios, LLC. (http://www.zivios.org)
 * @license     http://www.zivios.org/legal/license
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

class squid(ZiviosAgent.ZiviosAgent):
    def xmlrpc_getnetcfg(self):
        log.msg("squid getnetcfg called")
        file = self.getProperty('trustednetworks')
        FILE = open(file)
        lines = FILE.readlines()
        return lines

    def xmlrpc_setnetcfg(self, data):
        log.msg("squid setnetcfg called")
        file = self.getProperty('trustednetworks')
        FILE = open(file, "w")
        for line in data:
            FILE.write(line + "\n")
        log.msg(data)
        return True

    def xmlrpc_addService(self):
        print 'squid addService function called'

    def xmlrpc_serviceStatus(self):
        log.msg("getting service status")
        return self.checkProcess(self.getProperty('squidpidfile'))

    def xmlrpc_stopService(self):
        response,regexcode,exitcode = self.command("stopsquidcommand")
        return (exitcode == 0)
    
    def xmlrpc_startService(self):
        response,regexcode,exitcode = self.command("startsquidcommand")
        time.sleep(1)
        return (exitcode == 0)
    
    def xmlrpc_currentTime(self):
        now = datetime.datetime.now()
        return now.ctime()
