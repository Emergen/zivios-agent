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
import base64
import rpm

class package(ZiviosAgent.ZiviosAgent):
    
    def xmlrpc_getallrpmpackages(self):
        ts = rpm.TransactionSet();
        mi = ts.dbMatch()
	retlist = []
	for package in mi:
		iter = []
		iter.append(base64.b64encode(package['name']))
		iter.append(base64.b64encode(package['version']))
		iter.append(base64.b64encode(package['release']))
		iter.append(base64.b64encode(package['summary']))
		iter.append(base64.b64encode(package['description']))
		iter.append(base64.b64encode(",".join(package['requires'])))
		retlist.append(iter)
	return retlist
            
            
            
    
