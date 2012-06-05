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
from twisted.python import log
import ZiviosAgent

class samba(ZiviosAgent.ZiviosAgent):
    
    def xmlrpc_getstatus(self):
        return self.checkProcess(self.getProperty('sambapidfile'))
    
    
    def xmlrpc_startservice(self):
        resp,code,exit =  self.command("samba-start")
        return (exit==0)
        
    def xmlrpc_stopservice(self):
        resp,code,exit =  self.command("samba-stop")
        return (exit==0)
        
    


