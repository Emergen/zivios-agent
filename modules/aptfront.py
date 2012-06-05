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
 * @version		$Id: netfile.py 115 2008-09-10 09:46:39Z mhashmi $
 * @subpackage  Core
"""

from twisted.web import xmlrpc
from twisted.python import log
import os
import shutil
import base64
import grp
import pwd
import time
import ZiviosAgent
import threading
from twisted.internet import defer, protocol, reactor

class aptfront(ZiviosAgent.ZiviosAgent):
    package = None
    cache = None
    
    def xmlrpc_test(self):
        reactor.callInThread(aptfront.blocker,self)
        return "OK"
            
    def xmlrpc_install(self,package,transid):
        
        
        reactor.callInThread(self.doInstall,package,transid)
        return 1
        
    def doInstall(self,package,transid):
        resp,code,exit = self.command("installpkg",{"package":package})
        log.msg("Done Installing!")
        
    def doDelete(self,package,transid):
        resp,code,exit = self.command("deletepkg",{"package":package})
        log.msg("Done Delete")
        
    def xmlrpc_delete(self,package,transid):
        reactor.callInThread(self.doDelete,package,transid)
        return 1
                


