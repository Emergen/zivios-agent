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
import base64
from twisted.python import log

import ZiviosAgent,PtyHelper

class kerberos(ZiviosAgent.ZiviosAgent):

    def xmlrpc_setpw(self,uid,passwd,realm):
        pty = PtyHelper.PtyHelper(self.getProperty('kadmindconsole'),'kadmin> ')
        pty.immediateExpect('cpw ' + uid, uid + '@' + realm + '\'s Password: ', 10)
        pty.immediateExpect(passwd, 'Verifying - ' + uid + '@' + realm + '\'s Password: ',10)
        
        if pty.immediateExpect(passwd, 'kadmin> ', 5):
            pty.__del__()
            log.msg("kerberos setpw returning 1")
            return 1
        else:
            return 0

    def xmlrpc_setrandpw(self,host,realm):
        pty = PtyHelper.PtyHelper(self.getProperty('kadmindconsole'),'kadmin> ')
        if pty.immediateExpect('cpw --random-key '+host,'kadmin> ', 10):
            pty.__del__()
            log.msg("Kerberos Random Password Generated for host "+host)
            return 1
        else:
            return 0
    
    def xmlrpc_extractkeytab(self,principal):
        filename = "/tmp/keytab.tmp"
        resp,code,exit = self.command("extractkeytab",{"tmpktfile":filename,"principal":principal})
        if (exit == 0):
            fileHandle = open ( filename )
            data = fileHandle.read()
            fileHandle.close()
            os.remove(filename)
            return base64.b64encode(data)
        else:
            error = []
            error['errcode'] = 10
            error['message'] = 'Error in keytab extraction'
            error['code'] = 10
            return error

    def xmlrpc_listprinc(self):
        pty = PtyHelper.PtyHelper('/opt/ems/heimdal/sbin/kadmin -l','kadmin>')
        buf = pty.expect('list *','kadmin>',5)
        buf = buf.strip()
        buf = buf.split("\r\n")
        return buf
    
    def xmlrpc_startService(self):
        response,regexcode,exitcode = self.command("startkrbcommand")
        return exitcode

    def xmlrpc_startReplicaService(self):
        """
            ensure that krb5.conf is a symlink to:
              /opt/zivios/heimdal/etc/krb5.conf
        """
        if (os.path.isfile('/etc/krb5.conf')):
            os.remove('/etc/krb5.conf')
        elif (os.path.isdir('/etc/krb5.conf')):
            shutil.rmtree('/etc/krb5.conf')
        
        """
           create symlink
        """
        os.symlink('/opt/zivios/heimdal/etc/krb5.conf', '/etc/krb5.conf')
        
        response,regexcode,cyrusexitcode = self.command("startsasl")
        response,regexcode,krbexitcode = self.command("startkdccommand")

        return krbexitcode
    
    def xmlrpc_status(self):
        statusreport = []
        resp =  self.checkProcess(self.getProperty('kdcpidfile'))
        statusreport.append(resp)
        resp =  self.checkProcess(self.getProperty('kadminpidfile'))
        statusreport.append(resp)
        resp =  self.checkProcess(self.getProperty('kpasswdpidfile'))
        statusreport.append(resp)
        
        return statusreport

    def xmlrpc_stopKdc(self):
        response,regexcode,exitcode = self.command("stopkdccommand")
        time.sleep(1)
        return (exitcode == 0)

    def xmlrpc_startKdc(self):
        response,regexcode,exitcode = self.command("startkdccommand")
        time.sleep(1)
        return (exitcode == 0)

    def xmlrpc_startKadmind(self):
        response,regexcode,exitcode = self.command("startkadmindcommand")
        return (exitcode == 0)

    def xmlrpc_stopKadmind(self):
        response,regexcode,exitcode = self.command("stopkadmindcommand")
        time.sleep(1)
        return (exitcode == 0)

    def xmlrpc_startKpasswdd(self):
        response,regexcode,exitcode = self.command("startkpasswddcommand")
        time.sleep(1)
        return (exitcode == 0)

    def xmlrpc_stopKpasswdd(self):
        response,regexcode,exitcode = self.command("stopkpasswddcommand")
        time.sleep(1)
        return (exitcode == 0)

    def xmlrpc_currentTime(self):
        now = datetime.datetime.now()
        return now.ctime()

