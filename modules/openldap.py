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
import random
import pwd
import grp
import shutil
from twisted.python import log
import ZiviosAgent

class openldap(ZiviosAgent.ZiviosAgent):

    """
        Clean Configuration Dir
    """
    def cleanConfDir(self):
        log.msg("Recreating configuration directory for openldap")
        response,regexcode,exitcode = self.command("removeconfdir")
        response,regexcode,exitcode = self.command("createconfdir")
        return 0

    """
        Clean Data Dir
    """
    def cleanDataDir(self):
        log.msg("Recreating data directory for openldap")
        response,regexcode,exitcode = self.command("removedatadir")
        response,regexcode,exitcode = self.command("createdatadir")
        response,regexcode,exitcode = self.command("setdataperms")
        return 0

    """
        Set Configuration Dir Permissions
    """
    def setConfPerms(self):
        log.msg("Setting permissions on configuration directory")
        response,regexcode,exitcode = self.command("setconfperms")
        return 0

    """
        Initialize Replica Data
    """
    def xmlrpc_initializeReplicaData(self):
        log.msg("called initializeReplicaData")

        """
            Ensure slapd is not running
        """
        self.command("stopslapd")
        
        """
            Clean replica conf and data folders
        """
        self.cleanConfDir()
        self.cleanDataDir()

        response,regexcode,exitcode = self.command("inibaserepl")
        if exitcode==0:
            log.msg("1_cnbase injected successfully.")
        else:
            log.msg("error injecting 1_cnbase.ldif. Check slapd logs")
            return 1
        
        response,regex,exitcode = self.command("inimodulesrepl")
        if exitcode==0:
            log.msg("2_cnmodules injected successfully.")
        else:
            log.msg("error injecting 2_cnmodules.ldif. Check slapd logs")
            return 1

        """
            Set permissions on slapd.d
        """
        self.setConfPerms()

        """
            Start the slapd service before injecting the primary database
        """
        response,regex,exitcode=self.command("startslapd")
        time.sleep(3)
        
        """
            Inject the primary database LDIF
        """
        response,regex,exitcode = self.command("inipridbrepl")
        if exitcode==0:
            log.msg("3_primarydb injected successfully.")
        else:
            log.msg("error injecting 3_primarydb.ldif. Check slapd logs")
            return 1
        
        response,regex,exitcode=self.command("stopslapd")
        time.sleep(3)
        response,regex,exitcode=self.command("startslapd")
        time.sleep(3)
        
        response,regex,exitcode = self.command("inichaindbrepl")
        if exitcode==0:
            log.msg("4_chain injected successfully.")
        else:
            log.msg("error injecting 4_chain.ldif. Check slapd logs")
            return 1
        
        return 0

    """
        Start OpenLDAP service
    """
    def xmlrpc_startService(self):
        response,regexcode,exitcode = self.command("startslapd")
        return exitcode
        
    def xmlrpc_startReplicaServices(self):
        log.msg("Starting OpenLDAP replica services.")
        
        exitresponse = []

        response,regexcode,exitcode = self.command("startslapd")
        exitresponse.append(exitcode)

        response,regexcode,exitcode = self.command("startkrb")
        exitresponse.append(exitcode)

        response,regexcode,exitcode = self.command("startsasl")
        exitresponse.append(exitcode)
        
        """ exitcodes should be checked in order by caller """
        return exitresponse

    def xmlrpc_getReplicaServiceStatus(self):
        serviceStatus = []
        ldapStatus = self.checkProcess(self.getProperty('ldappidfile'));
        krbStatus  = self.checkProcess(self.getProperty('kdcpidfile'));
        saslStatus = self.checkProcess(self.getProperty('saslpidfile'));
        bindStatus = self.checkProcess(self.getProperty('bindpidfile'));

        serviceStatus.append(ldapStatus)
        serviceStatus.append(krbStatus)
        serviceStatus.append(saslStatus)
        serviceStatus.append(bindStatus)

        return serviceStatus

