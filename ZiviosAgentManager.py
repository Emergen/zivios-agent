#python!
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
import xmlrpclib
from twisted.internet.threads import deferToThread
from twisted.python import log
from twisted.web import xmlrpc, server, http
from twisted.internet import defer, protocol, reactor
import ldap
import logging
import os
import popen2
import base64
import re
from twisted.application import service, internet
from twisted.web import static, server
import sys
sys.path.append(os.environ['ZIVIOSAGENTHOME'])
from ConfigParser import *

Fault = xmlrpclib.Fault
from OpenSSL import SSL

class ServerContextFactory:
    
    def getContext(self):
        """Create an SSL context.
        This will load SSL Public and private certs from the file.
        """
        config = ConfigParser()
        apppath = os.environ['ZIVIOSAGENTHOME']
        config.read(apppath+"/config/ZiviosAgentManager.ini")
        cafile = config.get("general","sslcert")
        prvfile = config.get("general","sslprivatekey")
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.use_certificate_file(cafile)
        ctx.use_privatekey_file(prvfile)
        return ctx

class ZiviosAgentManager(xmlrpc.XMLRPC):
    plugins = []
    logfile = None
    config = ConfigParser()
    apppath = os.environ['ZIVIOSAGENTHOME']
    config.read(apppath+"/config/ZiviosAgentManager.ini")
    con = ldap.initialize('ldap://'+config.get("general","masterldap"))
    con.protocol_version = ldap.VERSION3
    apppath = os.environ['ZIVIOSAGENTHOME']
    os.chdir(apppath)
	
    """ HTTP Authentication Routing 
    LDAP Auth is currently employed for inbound HTTP Authentication """
	
    def init_ldap(self):
        self.con = ldap.initialize('ldap://'+self.config.get("general","masterldap"))
        self.con.protocol_version = ldap.VERSION3
        log.msg("Successfully connected to ldap://"+self.config.get("general","masterldap"))

    def __init__(self):
        xmlrpc.XMLRPC.__init__(self)
        self.getConfig()
        self.initLogger()
        self.initPlugins()
		
    def getConfig(self):
        """This will read the config file in the future"""
        config = ConfigParser()
        config.read('config/ZiviosAgentManager.ini')
        self.config = config
        
    def getProperty(self,name):
        return self.config.get('general',name)
        
    def initLogger(self):
        log.msg("Zivios Agent Manager Startup")
	
    def initPlugins(self):
        """Loop through the plugins directory and instantiate every plugin"""
        filelist = os.listdir(self.apppath+"/modules/")
        for f in filelist:
            impfile = f.split('.')
             
            if (impfile[0] != '' and impfile[0] != '__init__' and impfile[1] != 'pyc'):
                """log.msg("Importing and Instantiating :"+impfile[0])"""
                fullclass =  'modules.'+impfile[0]
                mod = __import__(fullclass)
                classobj = eval('mod.' + impfile[0] + '.' + impfile[0])
                classinstance = classobj(self.getProperty('distro'))
                self.putSubHandler(impfile[0],classinstance)
                self.plugins.append(impfile[0])
                log.msg("Added XMLRPC Handler :"+impfile[0])
	
    def render(self, request):
        user = request.getUser()
        passwd = request.getPassword()
       
        if user=='' and passwd=='':
                request.setResponseCode(http.UNAUTHORIZED)
                return 'Authorization required!'
        else:
                auth = 0
                try: 
                    self.init_ldap()
                    self.con.bind_s(user, passwd)
                    auth=1
                    self.con.unbind()
                except ldap.INVALID_CREDENTIALS:
                    print "Your username or password is incorrect."
                except ldap.INVALID_DN_SYNTAX:
                    print "BAD DN"
		except ldap.SERVER_DOWN, e:
		    log.err("Connection to Ldap server failed!")
		    
                except ldap.LDAPError, e:
                    if type(e.message) == dict and e.message.has_key('desc'):
                       log.err(e.message['desc'])
                    else: 
                       log.err(e)

                if auth==0:
                    request.setResponseCode(http.UNAUTHORIZED)
                    return 'Authorization Failed!'
                else:
                    log.msg('Authorization successful as '+user+' with pass :***')

		"""Default XMLRPC render routing, do not confuse!"""
		
        request.content.seek(0, 0)
        args, functionPath = xmlrpclib.loads(request.content.read())
        
        try:
            function = self._getFunction(functionPath)
        except Fault, f:
            self._cbRender(f, request)

     
        request.setHeader("content-type", "text/xml")
        defer.maybeDeferred(function, *args).addErrback(self._ebRender).addCallback( self._cbRender, request )

        return server.NOT_DONE_YET
        
    def xmlrpc_capabilities(self):
        return self.plugins
    
    def xmlrpc_restart(self):
        log.msg("Agent Restart Requested!")
        os.system("/etc/init.d/ziviosagent restart")
        
    def xmlrpc_shutdown(self):
        log.msg("Agent Shutdown Requested!")
        os.system("/etc/init.d/ziviosagent stop")        
        return 1
        
    def addPlugin(self, plugin):
		return none


application = service.Application("Zivios Agent Framework")
print "Zivios Agent starting Up with working directory :"+os.getcwd()+" and Port 7080"
r = ZiviosAgentManager()
xmlrpc_server = internet.SSLServer(7080, server.Site(r), ServerContextFactory())
xmlrpc_server.setServiceParent(application)

if __name__ == '__main__':
    print "Will not Start directly, please use the twistd application server"
    

