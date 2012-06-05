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
import shutil
import base64
import popen2
import re
import ZiviosAgent

class mail(ZiviosAgent.ZiviosAgent):
    
    
    def __init__(self,distrodef):
        ZiviosAgent.ZiviosAgent.__init__(self,distrodef)
       
        
    def xmlrpc_getactivequeue(self):
        messagedata = []
        
       
        
        senderre = re.compile("sender: (.+?)\n")
        timere = re.compile("message_arrival_time: (.+?)\n")
        recipientre = re.compile("recipient: (.+?)\n")
        reasonre = re.compile("reason=(.+?)\n")
        sizere = re.compile("message_size:(.+?)\n")
        active = self.getProperty('pfactiveqpath')
        
        filelist = os.listdir(active)
        for f in filelist:
            try:
                postcat = self.getProperty('postcat')
                fileHandle = os.popen( postcat +" "+active+"/"+f )
                data = fileHandle.read(1000)
                fileHandle.close()
                            
                messagedetails  = []
                sender = senderre.search(data)
                if (sender):
                    sender = sender.group(1)
                
                time = timere.search(data)
                if (time):
                    time = time.group(1)
                    
                recipient = recipientre.search(data)
                if (recipient):
                    recipient = recipient.group(1)
                
                size = sizere.search(data)
                if (size):
                    size = size.group(1)
                
                messagedetails.append(f)
                messagedetails.append(sender)
                messagedetails.append(time)
                messagedetails.append(recipient)
                messagedetails.append(size)
                
                messagedata.append(messagedetails)
            except (IOError,AttributeError):
                pass
                

    
        return messagedata
  
    def xmlrpc_getdeferredqueue(self):
        
        messagedata = []
        messageids = []
        
        
        senderre = re.compile("sender: (.+?)\n")
        timere = re.compile("message_arrival_time: (.+?)\n")
        recipientre = re.compile("recipient: (.+?)\n")
        reasonre = re.compile("reason=(.+?)\n")
        sizere = re.compile("message_size:(.+?)\n")
        
        deferred = self.getProperty('pfdeferredqpath')
        defer = self.getProperty('pfdeferqpath')
        
        
        dirlist = os.listdir(deferred)
        for d in dirlist:
            filelist = os.listdir(deferred+"/"+d)
            
            for f in filelist:
                try:
                    postcat = self.getProperty('postcat')
                    
                    fileHandle = os.popen( postcat + " "+deferred+"/"+d+"/"+f )
                    data = fileHandle.read(1000)
                    fileHandle.close()
                    
                    fileHandle = open ( defer+"/"+d+"/"+f )
                    delayreason = fileHandle.read()
                    fileHandle.close()
                
                
                    messagedetails  = []
                    
                    sender = senderre.search(data)
                    if (sender):
                        sender = sender.group(1)
                    
                    time = timere.search(data)
                    if (time):
                        time = time.group(1)                
    
                    recipient = recipientre.search(data)
                    if (recipient):
                        recipient = recipient.group(1)
                    
                    reason = reasonre.search(delayreason)
                    if (reason):
                        reason = reason.group(1)
                    
                    size = sizere.search(data)
                    if (size):
                        size = size.group(1)
                    
                    messagedetails.append(f)
                    messagedetails.append(sender)
                    messagedetails.append(time)
                    messagedetails.append(recipient)
                    messagedetails.append(reason)
                    messagedetails.append(size)
                    
                    messagedata.append(messagedetails)
                except (IOError,AttributeError):
                    pass
                    

        return messagedata
    
    def xmlrpc_startservice(self):
        statusreport = []
        resp,code,exit =  self.command("spamassassin-start")
        statusreport.append((exit==0))

        resp,code,exit = self.command("clamav-start")
        statusreport.append((exit==0))
        
        resp,code,exit = self.command("amavis-start")
        statusreport.append((exit==0))

        resp,code,exit = self.command("postfix-start")
        statusreport.append((exit==0))

        resp,code,exit = self.command("cyrus-start")
        statusreport.append((exit==0))
        
        

        return statusreport
        

    def xmlrpc_status(self):
        statusreport = {}
        
        resp =  self.checkProcess(self.getProperty('spamassassinpidfile'))
        statusreport['spamassassin']= resp

        resp =  self.checkProcess(self.getProperty('clamavpidfile'))
        statusreport['clamav'] = resp

        resp =  self.checkProcess(self.getProperty('amavispidfile'))
        statusreport['amavis'] = resp

        resp =  self.checkProcess(self.getProperty('postfixpidfile'))
        statusreport['postfix'] = resp
        
        resp = self.checkProcess(self.getProperty('cyruspidfile'))
        statusreport['cyrus'] = resp
        
        return statusreport
        
    def xmlrpc_stopservice(self):
        statusreport = []

        resp,code,exit = self.command("spamassassin-stop")
        statusreport.append((exit==0))
        
        resp,code,exit = self.command("clamav-stop")
        statusreport.append((exit==0))
        
        resp,code,exit = self.command("amavis-stop")
        statusreport.append((exit==0))
        
        resp,code,exit = self.command("postfix-stop")
        statusreport.append((exit==0))
        
        resp,code,exit = self.command("cyrus-stop")
        statusreport.append((exit==0))
        
        return statusreport        
        
    def xmlrpc_flushqueue(self):
        resp,code,exit = self.command("flushqueue")
        return code
        
      
    def xmlrpc_deletemessage(self,id):
        resp,code,exit = self.command("postsuperdelete",{"id":id})
        return code
         
            
    
