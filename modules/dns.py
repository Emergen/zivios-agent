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
import pwd
import grp
import shutil
from twisted.python import log
import ZiviosAgent,PtyHelper

class dns(ZiviosAgent.ZiviosAgent):

    def xmlrpc_stopDns(self):
        response,regexcode,exitcode = self.command("stopbindcommand")
        time.sleep(1)
        return (exitcode == 0)

    def xmlrpc_startDns(self):
        response,regexcode,exitcode = self.command("startbindcommand")
        time.sleep(1)
        return (exitcode == 0)
    
    def xmlrpc_iniReplica(self):
        """
            fix file permissions
        """
        """ hardcoded permissions! 
        numuid = pwd.getpwnam('zdnsuser')
        numuid = numuid[2]

        numgid = grp.getgrnam('zdns')
        numgid = numgid[2]
        """
        numuid = 952
        numgid = 952

        os.chown('/opt/zivios/bind/etc/defaults', numuid, numgid)
        os.chown('/opt/zivios/bind/etc/named.conf.local', numuid, numgid)
        os.chown('/opt/zivios/bind/etc/named.conf.options', numuid, numgid)
        os.chown('/opt/zivios/bind/etc/rndc.key', numuid, numgid)

        """
            start the bind dns service
        """
        response,regexcode,exitcode = self.command("startbindcommand")
        time.sleep(1)

        """
            Overwrite resolv.conf:
             copy 
              /opt/zivios/bind/etc/resolv.conf
             to
              /etc/resolv.conf
        """
        shutil.copy('/opt/zivios/bind/etc/resolv.conf', '/etc/resolv.conf')

        return exitcode
    
    def xmlrpc_status(self):
        resp =  self.checkProcess(self.getProperty('bindpidfile'))
        return resp

    def xmlrpc_currentTime(self):
        now = datetime.datetime.now()
        return now.ctime()

