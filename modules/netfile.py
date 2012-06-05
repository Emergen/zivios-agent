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

from twisted.web import xmlrpc
from twisted.python import log
import os
import shutil
import base64
import grp
import pwd
import ZiviosAgent

class netfile(ZiviosAgent.ZiviosAgent):

    def xmlrpc_get(self,filename):
        log.msg("Netfile reading and sending file "+filename)
        if (os.path.isfile(filename)):
            fileHandle = open (filename)
            data = fileHandle.read()
            fileHandle.close()
            return base64.b64encode(data)
        else:
            return False

    def xmlrpc_put(self,filename,data,perm=None,owneruser='root',ownergroup='root'):
        if (perm == None or perm == 0):
            perm=0600

        log.msg("Netfile Writing Filename : " + filename + " with permissions :"+str(perm))

        """ Ensure path to file exists on computer """
        tdir = os.path.dirname(filename)
        if (os.path.isdir(tdir) == False):
            """ Create dir """
            os.umask(0);
            if (os.makedirs(tdir,0755) == False):
                log.msg("Error creating directory: " + tdir)
                return False

        if (os.path.isfile(filename)):
            log.msg("File already exists. Backup and overwrite")
            shutil.move(filename,filename+".bak")

        if (owneruser == 0 or owneruser == ''):
            owneruser = 'root'
        
        if (ownergroup == 0 or ownergroup == ''):
            ownergroup = 'root'
                        
        fileHandle = open (filename ,'w')
        fileHandle.write(base64.b64decode(data))
        fileHandle.close()
        
        os.chmod(filename,perm)
        numuid = pwd.getpwnam(owneruser)
        numuid = numuid[2]
        
        numgid = grp.getgrnam(ownergroup)
        numgid = numgid[2]
        
        os.chown(filename,numuid,numgid)
        
        return 1
    
