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
 
import re
import select
import fcntl
import pty
import sys
import time
import os
import fcntl
import termios
import signal
from twisted.python import log

class PtyHelper:

    ptycommand = ''
    ptychildfd=None
    pid=None
    args=None
    inbuffer=''
    parent = child = None
    
    def __init__(self,command,readyprompt=None):

        userargs = command.split(' ')
        log.msg(userargs)
        command = userargs[0]
        self.ptycommand = command
        self.args = userargs
        #self.pid, self.parent = pty.fork()
        self.parent,self.child = os.openpty()
        
        self.pid = os.fork()
        
        
        if self.pid == 0:
            
            os.close(self.parent)
            os.dup2(self.child, 0) #sys.stdin = rc
            os.dup2(self.child, 1) #sys.stdout = wc
            os.dup2(self.child, 2) #sys.stderr = ec

            log.msg(self.args)
            os.execv(self.ptycommand,self.args)
        else:
            os.close(self.child)
            self.makeNonBlocking(self.parent)
            log.msg('bacha pid :'+str(self.pid))
            new = termios.tcgetattr(self.parent)
            new[3] = new[3] & ~termios.ECHO
            termios.tcsetattr(self.parent, termios.TCSANOW, new)
            #self.parent = fdopen(self.parent,'rw')
            if (readyprompt):
                self.expect(None,readyprompt)


                
    def close(self):
        if hasattr(termios, 'VEOF'):
           char = termios.tcgetattr(self.parent)[6][termios.VEOF]
        else:
            # platform does not define VEOF so assume CTRL-D
            char = chr(4)

        os.write(self.parent,char)        
        log.msg('fsync done')
        try:
            os.kill(self.pid,0)
        except OSError:
            log.msg('Child self-terminated.')
        else:
            log.msg('killing child '+str(self.pid))
            os.kill(self.pid,signal.SIGTERM)
            log.msg('signal sent, waiting for child to terminate')
            os.wait()

                
    def __del__(self):
        self.close()
    
    def makeNonBlocking(self,fd):
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        try:
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NDELAY)
        except AttributeError:
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | fcntl.FNDELAY)

    def immediateExpect(self,command,expregex,timeout=10):
        regex = re.compile("^"+re.escape(expregex)+"$")
        buf = self.expect(command,expregex,timeout,0)
        log.msg("Buf read in is: *"+buf+"*")
        if (regex.search(buf)): return 1
        else: return 0
        
    def expect(self,command,expregex,timeout=10,removeregex=1):
        read = None
        regex = re.compile(re.escape(expregex))
        self.inbuffer = ''
        if (command):
            os.write(self.parent,command+'\r')
        starttime = time.time()
        while(1):
            read = None
            
            ready = select.select([self.parent],[],[],0)
            if self.parent in ready[0]:
                read = os.read(self.parent,1024)
                
            else:
                if ((time.time() - starttime) > timeout): 
                    self.close()
                    raise Exception('Timeout waiting for regex match')
                else:
                    ready = select.select([self.parent],[],[],0.5)
                    if self.parent in ready[0]:
                        read = os.read(self.parent,1024)


            
            if (read != None):
                log.msg('read : '+read)
                self.inbuffer = self.inbuffer + read
                match = regex.search(self.inbuffer)
                if (match):
                    if (command):
                        log.msg('full buffer is '+self.inbuffer)
                        inmatch = re.compile(re.escape(command)+'\r')
                        self.inbuffer = inmatch.sub('',self.inbuffer)
                        self.inbuffer = self.inbuffer.lstrip()

                        log.msg('removed buffer is '+self.inbuffer)
                    if (removeregex): self.inbuffer = regex.sub('',self.inbuffer)
                    #os.flush(self.parent)
                    return self.inbuffer
                    
                    
                    
                    
                    
                    
                    
