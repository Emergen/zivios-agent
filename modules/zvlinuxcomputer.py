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
import logging
import os
import popen2
import re
import string
import time
import datetime
from twisted.python import log
import ZiviosAgent

class zvlinuxcomputer(ZiviosAgent.ZiviosAgent):
    
    def xmlrpc_probe_hardware(self):
        data = []

        cpu_resp,cpu_code,cpu_exit = self.command("probe-cpu")
        cpumhz_resp,cpumhz_code,cpumhz_exit = self.command("probe-cpumhz")
        cpucount_resp,cpucount_code,cpucount_exit = self.command("probe-cpucount")
        ram_resp,ram_code,ram_exit = self.command("probe-ram")
        swap_resp,swap_code,swap_exit = self.command("probe-swap")
        arch_resp,arch_code,arch_exit = self.command("probe-arch")
        release_resp,release_code,release_exit = self.command("probe-release")
        distro_resp,distro_code,distro_exit = self.command("probe-distro")
        codename_resp,codename_code,codename_exit=self.command("probe-codename")
        
        if cpu_exit==0:
            data.append(cpu_resp)
        else:
            data.append('NA')

        if cpumhz_exit==0:
            data.append(cpumhz_resp)
        else:
            data.append('NA')

        if cpucount_exit==0:
            data.append(cpucount_resp)
        else:
            data.append('NA')

        if ram_exit==0:
            data.append(ram_resp)
        else:
            data.append('NA')

        if swap_exit==0:
            data.append(swap_resp)
        else:
            data.append('NA')

        if arch_exit==0:
            data.append(arch_resp)
        else:
            data.append('NA')

        if release_exit==0:
            data.append(release_resp)
        else:
            data.append('NA')

        if distro_exit==0:
            data.append(distro_resp)
        else:
            data.append('NA')

        if codename_exit==0:
            data.append(codename_resp)
        else:
            data.append('NA')

        return data

    def xmlrpc_uptime(self):
        resp,code,exit = self.command("system-uptime")
        if exit==0:
            return resp
        else:
            return False

    def xmlrpc_shutdownSystem(self):
        resp,code,exit = self.command("system-shutdown")
        if exit==0:
            return True
        else:
            return False
    
    def xmlrpc_rebootSystem(self):
        resp,code,exit = self.command("system-reboot")
        if exit==0:
            return True
        else:
            return False
