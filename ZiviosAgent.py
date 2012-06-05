#python
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
 * @package     ZiviosAgent
 * @copyright   Copyright (c) 2008 Zivios, LLC. (http://www.zivios.org)
 * @license     http://www.zivios.org/legal/license
 * @subpackage  Core
"""

import xmlrpclib
from twisted.internet.threads import deferToThread
from twisted.web import xmlrpc, server, http
from twisted.python import log
from twisted.internet import defer, protocol, reactor
import ldap
import logging
import os
import os.path
import popen2
import base64
import re
import select
import pty
import sys

from ConfigParser import *

class ZiviosAgent(xmlrpc.XMLRPC):
    configuration = ''
    distrodef = ''
    
    def __init__(self,distrodef):
        pluginname = self.__class__.__name__
        log.msg(pluginname+" Plugin Registered")
        self.distrodef = distrodef
        configdict = SafeConfigParser()
        configdict.read('config/'+pluginname+'.ini')
        self.configuration = configdict

    def isPidRunning(self,pid):
        intpid = int(pid)
        log.msg("testing pid "+pid+" for running status")
        try:
            os.kill(intpid,0)
            return 1
        except OSError:
            return 0

    def checkProcess(self,pidfile):
    
        if (os.path.exists(pidfile)):
            fileHandle = open(pidfile)
            data = fileHandle.read()
            log.msg("read pid :"+data+" from pidfile :"+pidfile)
            return self.isPidRunning(data.strip())
        else:
            return 0

    def commandOnShell(self,popen4obj,command,endonregex):
        regex = re.compile(endonregex)
        
        outfile = popen4obj.fromchild 
        errfile = popen4obj.childerr
        outfd = outfile.fileno()
        errfd = errfile.fileno()
        infile = popen4obj.tochild
        infile.write(command)
        infile.flush()
       
        self.makeNonBlocking(outfd)            # don't deadlock
        self.makeNonBlocking(errfd)
        outdata = errdata = ''
        outeof = erreof = 0
        while 1:
            ready = select.select([outfd,errfd],[],[]) # wait for input
            if outfd in ready[0]:

                log.msg('attempting to read')
                outchunk = outfile.read()
                if outchunk == '': outeof = 1
                outdata = outdata + outchunk
                end = regex.search(outdata)
                log.msg('read :'+outchunk)
                
            if errfd in ready[0]:
                errchunk = errfile.read()
                if errchunk == '': erreof = 1
                errdata = errdata + errchunk
                log.msg('read err:'+errchunk)

            if outeof : break
            if end : break
            select.select([],[],[],.1) # give a little time for buffers to fill
            
        #if err != 0: 
        #raise RuntimeError, '%s failed w/ exit code %d\n%s' % (command, err, errdata)
        return outdata
    
    def getProperty(self,name,dictionary=None):
        return self.configuration.get(self.distrodef,name,0,dictionary)
    
    def getGeneralProperty(self,name,dictionary=None):
        return self.configuration.get('general',name,0,dictionary)
        
    """
        command needs the command name which it will extract from the module
        config file and a dictionary which needs to be expanded
        """
    
    def command(self,cmdname,dictionary=None,baseenc=0):
        cmd = self.getProperty(cmdname,dictionary)
        cmdcheckregex = self.getProperty(cmdname+".success",dictionary)
        regex = re.compile(cmdcheckregex)
        log.msg("running command :"+cmd+" and regex success match is :"+cmdcheckregex+"\n")
        
        popen = popen2.Popen4(cmd)
        filehandle = popen.fromchild
        exitcode = popen.wait()
        resp = filehandle.read()
        filehandle.close()
        popen.tochild.close()
        success = regex.search(resp)
        if (success):
            regexcode = 1
        else:
            regexcode = 0
            
        log.msg("Command returned: "+resp+" | regex response "+str(regexcode)+" | exitcode "+str(exitcode))
        
        if (baseenc):
            return base64.encodestring(resp),regexcode,exitcode
        else: 
            return resp,regexcode,exitcode

