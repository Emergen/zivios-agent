from twisted.web import xmlrpc
from twisted.python import log
import os
import time
import re
import base64
import csv

import ZiviosAgent

class asterisk(ZiviosAgent.ZiviosAgent):
    
	def __init__(self,distrodef):
		ZiviosAgent.ZiviosAgent.__init__(self,distrodef)
		global CMD_PATH
		CMD_PATH = '/opt/zivios/asterisk/bin/'				##path where perl scripts resides
		global CMD_GS 
		CMD_GS = CMD_PATH + 'getsection' 			##get section of a file filtered by key
		global CMD_GSFV
		CMD_GSFV = CMD_PATH + 'getsectionfval'		##get section of a file filtered by value
		global CMD_GFS 
		CMD_GFS = CMD_PATH + 'getformattedsection'	##get section of a file in key => value formatting
		global CMD_GL
		CMD_GL = CMD_PATH + 'getlist'				##get list of all sections in a file

	def xmlrpc_gettrunks(self):

		p = os.popen(CMD_GS + " --name extensions --section=globals --filter TRUNK")
		output = p.read()
		output = output.strip()
		output = output.split("\n")
		return output

	def xmlrpc_getparking(self):
		
		p = os.popen(CMD_GS + " --name features --section=general --filter n")
		output = p.read()
		return output


	def xmlrpc_setparking(self,parkext,parkpos,parkingtime):
		
		p = os.popen(CMD_PATH + "featuresstub --parkext='"+parkext+"' --parkpos='"+parkpos+"' --parkingtime="+parkingtime)
		output = p.read()
		self.reload()
		return output

	def xmlrpc_addsiptrunk(self,aob,DirtyParams=None):
		type = aob[0]
		name = aob[1]
		user = aob[2]
		authuser = aob[3]
		secret = aob[4]
		host = aob[5]
		port = aob[6]
		auth = aob[7]
		clid = aob[8]
		qualify = aob[9]
		allow = aob[10]
		if isinstance(allow, list) == 1:
			allow = " ".join(allow)
		expiry = aob[11]
		dtmfmode = aob[12]
		delonot = aob[13]
		insecure = aob[14]
		if DirtyParams != None:
			pd = os.popen(CMD_PATH + 'delsip --name=' + DirtyParams[0] + ' --username=' + DirtyParams[1] + ' --trunk --register')
			log.msg(CMD_PATH + 'delsip --name=' + DirtyParams[0] + ' --username=' + DirtyParams[1] + ' --trunk --register')
			time.sleep(1)
		p = os.popen(CMD_PATH + "addsip --name "+name+" --secret "+secret+" --type "+type+" --host "+host+" --authuser "+authuser+" --username "+user+" --register --allow '"+allow+"' --insecure "+insecure+" --context TRUNK_"+name+" --trunk --port "+port+" --dtmfmode="+dtmfmode+" --qualify "+qualify+" --expiry="+expiry+" --callerid '"+ clid + "'")
		log.msg(CMD_PATH + "addsip --name "+name+" --secret "+secret+" --type "+type+" --host "+host+" --authuser "+authuser+" --username "+user+" --register --allow '"+allow+"' --context TRUNK_"+name+" --trunk --port "+port+" --dtmfmode="+dtmfmode+" --qualify "+qualify+" --expiry="+expiry+" --callerid '"+ clid + "'")
		self.reload()
		return 1

	def xmlrpc_gettrunk(self, trunk, type):
		output = None
		log.msg("initializing gettrunk")
		if type == 'sip':
			p = os.popen(CMD_GS + " --name sip --section " + trunk + " --filter n")
			output = p.read()
		if type == 'iax':
			p = os.popen(CMD_GS + " --name iax --section " + trunk + " --filter n")
			output = p.read()
		log.msg(output.strip())
		return output.strip()

	def xmlrpc_addiaxtrunk(self,aob,DirtyParams=None):
		for line in aob:
			print line
			
		delonot = None
		type = aob[0]
		name = aob[1]
		user = aob[2]
		authuser = aob[3]
		secret = aob[4]
		host = aob[5]
		port = aob[6]
		authmode = aob[7]
		inkeys = aob[8]
		clid = aob[9]
		qualify = aob[10]
		trunking = aob[11]
		jitterbuffer = aob[12]
		allow = aob[13]
		if isinstance(allow, list) == 1:
			allow = " ".join(allow)
		expiry = aob[14]
		dtmfmode = aob[15]
		delonot = aob[16]
		if DirtyParams != None:
			pd = os.popen(CMD_APTH + 'deliax --name=' + DirtyParams[0] + ' --username=' + DirtyParams[1] + ' --trunk --register')
			log.msg(CMD_PATH + '/deliax --name=' + DirtyParams[0] + ' --username=' + DirtyParams[1] + ' --trunk --register')
			time.sleep(1)
		p = os.popen(CMD_PATH + "addiax --name "+name+" --secret "+secret+" --type "+type+" --host '"+host+"' --expiry="+expiry+" --username "+user+" --authuser="+authuser+" --register --allow '"+allow+"' --context TRUNK_"+name+" --trunk --port "+port+" --qualify "+qualify+" --callerid '"+ clid + "' --auth="+ authmode + " --inkeys=" +inkeys+" --trunking="+trunking+" --jb="+jitterbuffer)
		log.msg(CMD_PATH + "addiax --name "+name+" --secret "+secret+" --type "+type+" --host '"+host+"' --expiry="+expiry+" --username "+user+" --authuser="+authuser+" --register --allow '"+allow+"' --context TRUNK_"+name+" --trunk --port "+port+" --qualify "+qualify+" --callerid '"+ clid + "' --auth="+ authmode + " --inkeys=" +inkeys+" --trunking="+trunking+" --jb="+jitterbuffer)		
		self.reload()
		return 1

	def xmlrpc_getobroutes(self, filter=None):
		result = []
		if filter: ##check if probing for a single outbounf route
			try:
				p = os.popen(CMD_GSFV + " --name extensions --section=outbound --filter='"+filter+"'")
				log.msg(CMD_GSFV + " --name extensions --section=outbound --filter='"+filter+"'")
				output = p.read()	
				output = output.split("=>")
				output = output[1].strip()
				output = output.split(" ")
				extenre= re.compile('^(.*),([a-zA-Z0-9]),(.*)\((.*),(.*),([0-9]*)\${EXTEN:([0-9])},(.*)\)')
				for line in output:
					subresult = []
					t = extenre.match(line)
					subresult.append(t.group(1))
					subresult.append(t.group(5))
					subresult.append(t.group(6))
					subresult.append(t.group(7))
					subresult.append(t.group(8))
					result.append(subresult)
			except:
				pass
		else:			
			try:
				p = os.popen(CMD_GS + " --name extensions --section=outbound --filter n")
				log.msg(CMD_GS + " --name extensions --section=outbound --filter n")
				output = p.read()	
				output = output.split("=>")
				output = output[1].strip()
				output = output.split(" ")
				extenre= re.compile('^(.*),([a-zA-Z0-9]),(.*)\((.*),(.*),([0-9]*)\${EXTEN:([0-9])},(.*)\)')
				for line in output:
					subresult = []
					t = extenre.match(line)
					subresult.append(t.group(1))
					subresult.append(t.group(5))
					subresult.append(t.group(6))
					subresult.append(t.group(7))
					subresult.append(t.group(8))
					result.append(subresult)
			except:
				pass
		return result

	def xmlrpc_addcallrule(self, Pattern, Name, Trunk, Prepend, Skip, New=0):
		if New != 0:
			p = os.popen(CMD_PATH+"delobroute --pattern='"+ New +"'")
			log.msg(CMD_PATH+"delobroute --pattern='"+ New +"'")
			time.sleep(1)
		
		CRoute = self.xmlrpc_checkextension('_'+Pattern)
		log.msg(CRoute)
		if CRoute!=0:
			err = {}
			err['errcode'] = 100
			err['message'] = 'pattern/extension ' + CRoute + ' already exists'
			return err
		else:
			p = os.popen(CMD_PATH+"addobroute --name='"+Name+"' --trunk='"+Trunk+"' --pattern='"+Pattern+"' --prepend='"+Prepend+"' --skip="+Skip)
			log.msg(CMD_PATH+"addobroute --name='"+Name+"' --trunk='"+Trunk+"' --pattern='"+Pattern+"' --prepend='"+Prepend+"' --skip="+Skip)
			self.reload()
			return 1


	def xmlrpc_addincommingrule(self, Name,Pattern,Destination, New=0):
		if isinstance(New, list) == 1:
			p = os.popen(CMD_PATH+"delibroute --name='"+ New[2] +"' --pattern='"+New[1]+"' --dest='"+New[0]+"'")
			log.msg(CMD_PATH+"delibroute --name='"+ New[2] +"' --pattern='"+New[1]+"' --dest='"+New[0]+"'")
			time.sleep(1)
		
		p = os.popen(CMD_PATH+"addibroute --name='"+Name+"' --destiny='"+Destination+"' --exten="+Pattern)
		log.msg(CMD_PATH+"addibroute --name='"+Name+"' --destiny='"+Destination+"' --exten="+Pattern)
		self.reload()
		return 1

	def xmlrpc_getibroutes(self):
		root = []
		p = os.popen(CMD_GL + " --name extensions --type TRUNK")
		output = p.read()
		output = output.strip()
		output = output.split("\n")
		extenre = re.compile("^(.*),2,Goto\((.*)\)")
		for line in output:
			p = os.popen(CMD_GSFV + " --name extensions --section='"+ line +"' --filter '(.*),2'")
			subout = p.read()
			if subout.strip() == "":
				continue
			log.msg(subout)
			subout = subout.split("=>")
			subout = subout[1].strip()
			subout = subout.split(" ")
			for subline in subout:
				sube = []
				sube.append(line)
				subout = extenre.match(subline)
				sube.append(subout.group(1))
				sube.append(subout.group(2))
				root.append(sube)
		return root
	
	def xmlrpc_getibroute(self, Trunk, Did):
		p = os.open(CMD_GSFV + " --name extensions --section TRUNK_"+Trunk+" --filter "+Did+",2")
		subout = p.read()
		subout = subout.split("=>")
		subout = subout[1].strip()
		subout = subout.split(" ")		
		
		return subout

	def xmlrpc_delibroute(self, Trunk, Did, Dest):
		p = os.popen(CMD_PATH+"delibroute --name='"+ Trunk +"' --pattern='"+Did+"' --dest='"+Dest+"'")
		log.msg(CMD_PATH+"delibroute --name='"+ Trunk +"' --pattern='"+Did+"' --dest='"+Dest+"'")
		self.reload()
		return 1

	def xmlrpc_delcallrule(self, RulePattern):
		p = os.popen(CMD_PATH+"delobroute --pattern='"+ RulePattern +"'")
		log.msg(CMD_PATH+"delobroute --pattern='"+ RulePattern +"'")
		self.reload()
		return 1

	def xmlrpc_deltrunk(self, type, name, username):
		if type == 'sip':
			pd = os.popen(CMD_PATH+'delsip --name=' + name + ' --username=' + username + ' --trunk --register --ibroutes')
			log.msg(CMD_PATH+'delsip --name=' + name + ' --username=' + username + ' --trunk --register')
			
		if type == 'iax':
			pd = os.popen(CMD_PATH+'deliax --name=' + name + ' --username=' + username + ' --trunk --register --ibroutes')
			log.msg(CMD_PATH+'deliax --name=' + name + ' --username=' + username + ' --trunk --register')
			
		self.reload()
		return 1

	def xmlrpc_getivr(self, Name=None):
		extenre = re.compile('^(.*),(.*),(.+?)(\(.*)$')
		extre = re.compile('([0-9])')
		ivrlist = []
		if Name==None:
			Name = 'ivr'
		ps = os.popen(CMD_GL + " --name extensions --type="+Name)
		output = ps.read()
		try:
			output = output.strip()
			output = output.split("\n")
			for ivr in output:
				log.msg(ivr)
				paramlist = []
				optiondict = {}
				paramlist.append(ivr)
				ps = os.popen(CMD_GFS + " --name=extensions --section="+ivr+" --filter=n")
				subout = ps.read();		
				subout = subout.strip()
				subout = subout.split("\n")				
				for exten in subout:
					log.msg(exten)
					try:
						LocalExten = None
						t = extenre.match(exten)
						ext = t.group(1)
						priority = t.group(2)
						app	= t.group(3)
						data = t.group(4)
					except AttributeError, e:
						log.msg(e, exten)
						if exten == 'internal':
							LocalExten = 'yes'
					data = data.lstrip('(').rstrip(')')
					if app == 'Set' and ext == 's':
						dvar,dval = data.split('=')
						log.msg(dvar, dval)
						if dvar == 'TIMEOUT(digit)':
							paramlist.append(dval)
						if dvar == 'TIMEOUT(response)':
							paramlist.append(dval)
						if dvar == 'LOOPCOUNT':
							paramlist.append(dval)
					if app == 'Background':
						paramlist.append(data)
					if (app == 'Goto') and (extre.search(ext)):
						log.msg(data + " found")
						optiondict[ext] = data
				paramlist.append(optiondict)
				if LocalExten != None:
					paramlist.append(LocalExten)
				ivrlist.append(paramlist)
			log.msg(ivrlist)
			return ivrlist
		except:
			log.msg('no ivr found')
			return ivrlist

	def xmlrpc_getdp(self, type='all',Skip=None):
		root = []
		if (type == 'ivr' or type == 'all') and Skip!='ivr':
			log.msg('listing ivr')
			p = os.popen(CMD_GL + " --name extensions --type ivr")
			output = p.read()
			output = output.strip()
			output = output.split("\n")
			for line in output:
				if line!="":
					child = []
					child.append(line)
					child.append(line + ',s,1')
					child.append('IVR')
					root.append(child)
		if (type == 'queues' or type == 'all') and Skip!='queues':
			log.msg('listing queues')
			p = os.popen(CMD_GS + " --name extensions --section queues --filter n")
			output = p.read()	
			try:
				output = output.split("=>")
				output = output[1].strip()
				output = output.split(" ")
				extenre = re.compile('^([0-9]*),1,([a-zA-Z]+)\(([a-zA-Z0-9]*)||||(.*)\)')
				for line in output:
					child = []
					li = extenre.match(line)
					if li.group(2) == 'Queue':
						exten = li.group(1)
						queue = li.group(3)
						child.append(exten)
						child.append('internal,' + exten + ',1')
						child.append('Queue')
						root.append(child)
			except:
				log.msg('nothing found in queues context')
				
		if (type == 'confs' or type == 'all') and Skip!='confs':
			log.msg('listing confs')
			p = os.popen(CMD_GS + " --name extensions --section confs --filter n")
			log.msg(CMD_GS + " --name extensions --section confs --filter n")
			output = p.read()	
			try:
				output = output.strip()
				output = output.split("=>")
				output = output[1].strip()
				output = output.split(" ")
				log.msg(output)
				extenre = re.compile('^([0-9]*),1')
				for line in output:
					child = []
					try:
						li = extenre.match(line)
						li = li.group(1)
						child.append(li)
						child.append('internal,'+li+',1')
						child.append('Conference')
						root.append(child)
					except:
						log.msg('Nothing actually found')
			except:
				log.msg('Nothing found here')
			
		if (type == 'outbound' or type == 'all') and Skip!='outbound':
			try:
				log.msg('listing outbound')
				p = os.popen(CMD_GS + " --name extensions --section outbound --filter exten")
				log.msg(CMD_GS + " --name extensions --section outbound --filter exten")
				output = p.read()	
				output = output.split("=>")
				output = output[1].strip()
				output = output.split(" ")
				extenre = re.compile('^(.*),1,(.*)')
				for line in output:
					child = []
					li = extenre.match(line)
					li = li.group(1)
					child.append(li)
					child.append('outbound,'+li+',1')
					child.append('Route')
					root.append(child)
			except:
				log.msg('nothing found here')
			
		if (type == 'internal' or type == 'all') and Skip!='internal':
			try:
				log.msg('listing internal')
				p = os.popen(CMD_GS + " --name extensions --section internal --filter exten")
				output = p.read()	
				output = output.split("=>")
				output = output[1].strip()
				output = output.split(" ")
				extenre = re.compile('^([0-9]*),')
				for line in output:
					child = []
					li = extenre.match(line)
					li = li.group(1)
					child.append(li)
					child.append('internal,'+li+',1')
					child.append('Extension')
					root.append(child)
			except:
				log.msg('nothing found here')
				
		if (type == 'voicemail' or type == 'all') and Skip!='voicemail':
			try:
				log.msg('listing voicemail')			
				p = os.popen(CMD_GS + " --name extensions --section voicemail --filter n")
				output = p.read()	
				output = output.split("=>")
				output = output[1].strip()
				output = output.split(" ")
				extenre = re.compile('^(.*),')
				for line in output:
					child = []
					li = extenre.match(line)
					li = li.group(1)
					child.append(li)
					child.append('internal,'+li+',1')
					child.append('Voicemail')
					root.append(child)
			except:
				log.msg('nothing found');
		log.msg(root)
		return root

	def xmlrpc_getsounds(self):
		
		files = os.listdir('/var/lib/asterisk/sounds/custom')
		return files

	def	xmlrpc_removesound(self, FileName):
		file = '/var/lib/asterisk/sounds/custom/' + FileName
		os.remove(file)
		return 1

	def xmlrpc_addivr(self, Name,ResTimeout,DigTimeout,Loop, LocalExten,PlayFile,Options,Modify):
		opts = ' '
		if Modify == 'yes':
			delp = os.popen(CMD_PATH+'delattendant --name=\'ivr-' + Name + '\'')
			log.msg(CMD_PATH+'delattendant --name=\'ivr-' + Name + '\'')
			time.sleep(1)
		if isinstance(Options, dict): 
			for o,v in Options.iteritems():
				opts = opts + " --option='"+o+" goto "+v+"'"
		else:
			for o,v in enumerate(Options):
				opts = opts + " --option='"+`o`+" goto "+v+"'"
				
		cmd = CMD_PATH+"addattendant --name="+Name \
		+" --res_timeout="+ResTimeout+" --dig_timeout="+DigTimeout+" --loop="+Loop \
		+" --playfile="+PlayFile+" --localext="+LocalExten+ " " + opts
		log.msg(cmd)
		p = os.popen(cmd)
		self.reload()
		return 1

	def	xmlrpc_removeivr(self, Name):
		
		delp = os.popen(CMD_PATH+'delattendant --name=\''+ Name + '\'')
		log.msg(CMD_PATH+'delattendant --name=\'' + Name + '\'')
		self.reload()
		
		return 1
	
	def xmlrpc_getqueues(self, Name='n'):
		queues = {}
		pq = os.popen(CMD_GFS + " --name=extensions --section=queues --filter='"+Name+"'" )
		qre = re.compile('^(.*),(.*),Queue\((.*)\)')
		tdre = re.compile('^(.*),2,Goto\((.*)\)')
		output = pq.read()
		output = output.split('\n')
		for line in output:
			try:
				fout = qre.match(line)
				log.msg(fout.groups())
				Queue = fout.group(3)
				Queue,junk,junk,junk,qtimeout = Queue.split('|')
				Exten = fout.group(1)
				queues[Exten] = None
				queues[Exten] = {}
				queues[Exten]['name'] = Queue
				queues[Exten]['qtimeout'] = qtimeout
				
				p = os.popen(CMD_GS + " --name queues --section "+Queue+" --filter n")
				log.msg(CMD_GS + " --name queues --section "+Queue+" --filter n")
				qoutput = p.read()
				qoutput = qoutput.strip()
				qoutput = qoutput.split('\n')
				for qparams in qoutput:
					key,val = qparams.split(' => ')
					log.msg(key, val)
					queues[Exten][key] = val
					
			except:
				if tdre.search(line):
					log.msg('got Timeout Destination')
					tdest = tdre.match(line)
					queues[tdest.group(1)]['timeoutdest'] = tdest.group(2)
				log.msg(line)
		return queues

	def xmlrpc_addqueue(self, Params=None, DirtyParams=None):
		if DirtyParams!=None:
			log.msg('dirty params found, lets do a cleanup first ;)')
			self.xmlrpc_delqueue(DirtyParams[0], DirtyParams[1])
			
		if Params!=None:
			CExten = self.xmlrpc_checkextension(Params['exten'])
			if CExten!=0:
				err = {}
				err['errcode'] = 100
				err['message'] = 'extension ' + CExten + ' already exists'
				return err
			else:
				str = '';
				log.msg(Params)
				for k,v in Params.iteritems():
					if k == 'members':
						v = " ".join(v)
					str = str + ' --' + k + '=\'' + v + '\''
				log.msg(str)
				p = os.popen(CMD_PATH + "addqueue " + str)
				self.reload()
				return 1

	def	xmlrpc_delqueue(self, Name, Exten):
		p = os.popen(CMD_PATH + "delqueue --name='" +Name+ "' --exten='"+Exten+"'")
		log.msg(CMD_PATH + "delqueue --name='" +Name+ "' --exten='"+Exten+"'")
		self.reload()
		return 1

	def xmlrpc_delsip(self, Exten):
		if Exten!=None:
			pd = os.popen(CMD_PATH + 'delsip --username=' + Exten)
			log.msg(CMD_PATH + 'delsip --username=' + Exten)
		return 1


	def xmlrpc_getconferences(self, Name=None):
		Rooms = []
		if Name==None:
			Name = 'n'
		p = os.popen(CMD_GFS + ' --name meetme --section rooms --filter ' + Name)
		log.msg(CMD_GFS + ' --name meetme --section rooms --filter ' + Name)
		output = p.read().strip()
		output = output.split('\n')
		for line in output:
			Room = []
			r = line.split(',')
			if r[0] != '':
				Room.append(r[0])
			try:
				Room.append(r[1])
			except:
				log.msg('no user password required')
			try:
				Room.append(r[2])
			except:
				log.msg('no admin password required')
			Rooms.append(Room)
		return Rooms

	def xmlrpc_addconference(self, Room,Pin,AdminPin,DirtyParam=None):
		if DirtyParam!=None:
			log.msg('dirty params found, lets do a cleanup first ;)')
			self.xmlrpc_removeconference(DirtyParam)
			
		CExten = self.xmlrpc_checkextension(Room)
		if CExten!=0:
			err = {}
			err['errcode'] = 100
			err['message'] = 'extension ' + Room + ' already exists'
			return err
		p = os.popen(CMD_PATH + "addmeetme --exten='" +Room+ "' --pin='"+Pin+"' --admpin='"+AdminPin+"'")
		log.msg(CMD_PATH + "addmeetme --exten='" +Room+ "' --pin='"+Pin+"' --admpin='"+AdminPin+"'")
		self.reload()
		return 1

	def xmlrpc_removeconference(self, Room):
		p = os.popen(CMD_PATH + "delmeetme --exten='" +Room+ "'")
		log.msg(CMD_PATH + "delmeetme --exten='" +Room+ "'")
		self.reload()
		return

	def xmlrpc_getvmsetup(self):
		VmSetup = {}
		vm = os.popen(CMD_GS + ' --name voicemail --section general --filter n')
		output = vm.read()
		output = output.strip()
		log.msg(output)
		output = output.split('\n')
		for line in output:
			log.msg(line)
			key,val = line.split(' => ')
			log.msg(key, val)
			VmSetup[key] = val
			
		evm = os.popen(CMD_GFS + ' --name extensions --section voicemail --filter n')
		log.msg(CMD_GFS + ' --name extensions --section voicemail --filter n')
		output = evm.read()
		output = output.strip()
		output = output.split('\n')
		log.msg(output)
		for line in output:
			log.msg(line)
			line = line.strip()
			if line!='':
				tline = line.split(',')
				if len(tline[2]) > 15:
					VmSetup['selfexten'] = tline[0]
				else:
					VmSetup['exten'] = tline[0]
		log.msg(VmSetup)
		return VmSetup

	def xmlrpc_updatevm(self, Params):
		TExten = Params['exten']
		TSelfExten = Params['selfexten']
		CExten = self.xmlrpc_checkextension(TExten)
		CSelfExten = self.xmlrpc_checkextension(TSelfExten)
		if CExten!=0:
			err = {}
			err['errcode'] = 100
			err['message'] = 'extension ' + CExten + ' already exists'
			return err
		elif CSelfExten!=0:
			err = {}
			err['errcode'] = 100
			err['message'] = 'extension ' + CSelfExten + ' already exists'
			return err
		else:
			str = ''
			for k,v in Params.iteritems():
				str = str + ' --' + k + '=\'' + v + '\''
			uvm = os.popen(CMD_PATH + 'voicemailstub ' + str)
			log.msg(CMD_PATH + 'voicemailstub ' + str)
			self.reload()
			return 1

	def xmlrpc_getstatus(self):
		status = self.checkProcess(self.getProperty('asteriskpid'))
		log.msg(status)
		return status

	def xmlrpc_adduser(self, Params):

		CExten = self.xmlrpc_checkextension(Params['exten'])
		if CExten!=0 and Params['exten']!=Params['oexten']:
			err = {}
			err['errcode'] = 100
			err['message'] = 'extension ' + CExten + ' already exists'
			return err
		else:
			if Params['oexten']!='':
				AU = os.popen(CMD_PATH + "deluser --user " + Params['oexten'] + " --exten " + Params['oexten'])
				log.msg(CMD_PATH + "deluser --user " + Params['oexten'] + " --exten " + Params['oexten'])
		
			Clid = Params['name'] +" <"+Params['exten']+">"
			Codecs = " ".join(Params['codecs'])
			time.sleep(1)
			cmd = CMD_PATH + "addsip --username " + Params['exten'] + " --exten " + Params['exten'] + " --allow '"+Codecs+"' --host=dynamic --type=friend --secret="+Params['secret']+" --context=internal --callerid='" + Clid + "'"
			if Params['vmpass']!='':
				cmd = cmd + " --mailbox=" + Params['exten']
				p = os.popen(CMD_PATH + "addvoicemail --exten=" + Params['exten'] + " --email='" + Params['email'] + "' --name='" + Params['name'] + "' --secret=" + Params['secret'])
				log.msg(CMD_PATH + "addvoicemail --exten=" + Params['exten'] + " --email='" + Params['email'] + "' --name='" + Params['name'] + "' --secret=" + Params['secret'])
			else:
				p = os.popen(CMD_PATH + "addvoicemail --exten=" + Params['oexten'] + " --email=" + Params['email'] + " --name='" + Params['name'] +"'")
				
			log.msg(cmd)
			AU = os.popen(cmd)	
			Routes = self.xmlrpc_getrouteperm()
			if len(Params['routes'])>0:
				if isinstance(Params['routes'], list):
					newRoute = Params['routes']
				else:
					newRoute = []
					newRoute.append(Params['routes'])
				newRoute.insert(0, Params['exten'])
				writer = csv.writer(open("/etc/asterisk/zivi.conf", "wb"))
				for Route in Routes:
					if Route[0] == Params['exten']:
						Routes.remove(Route)
				Routes.append(newRoute)
				writer.writerows(Routes)
			else:
				writer = csv.writer(open("/etc/asterisk/zivi.conf", "wb"))
				for Route in Routes:
					if Route[0] == Params['exten']:
						Routes.remove(Route)
				writer.writerows(Routes)
			self.reload()
			return 1

	def xmlrpc_getuser(self, Extension):
		exten = {}
		p = os.popen(CMD_GS + " --name sip --section "+Extension+" --filter n")
		log.msg(CMD_GS + " --name sip --section "+Extension+" --filter n")
		qoutput = p.read()
		qoutput = qoutput.strip()
		qoutput = qoutput.split('\n')
		for qparams in qoutput:
			if qparams=="":
				continue
			key,val = qparams.split(' => ')
			log.msg(key, val)
			exten[key] = val	
		p = os.popen(CMD_GS + " --name voicemail --section default --filter "+Extension)
		log.msg(CMD_GS + " --name voicemail --section default --filter "+Extension)
		vmout = p.read()
		vmout = vmout.strip()
		if vmout!="":
			vmout = vmout.split(' => ')
			vmout = vmout[1].split(',')
			exten['vmpass'] = vmout[0]
		
		exten['routes'] = self.xmlrpc_getrouteperm(Extension)
		return exten

	def xmlrpc_getrouteperm(self, Extension=None):
		readerobj = csv.reader(open("/etc/asterisk/zivi.conf", "r"))
		result = []
		if (Extension!=None):
			for row in readerobj:
				log.msg('getting single entry')
				if (row[0]==Extension):
					for i in range(1, len(row)):
						result.append(row[i])
			return result
		else:
			for row in readerobj:
				log.msg('whats up')
				result.append(row)
			return result

	def xmlrpc_getnextexten(self, Type='internal' ,Exten=None):
		try:
			if Exten==None:
				Exts = self.xmlrpc_getdp(Type)
				Ext = Exts[len(Exts) - 1][0]
			else:
				Ext = Exten
				
			log.msg(Ext)
			Ext = int(Ext) + 1
			Ext = str(Ext)
			log.msg('checking exten: ' + Ext)
			Test = self.xmlrpc_checkextension(Ext)
			log.msg('test result : ' + str(Test))
			if (str(Test)==Ext):
				log.msg('re check exten now')
				return self.xmlrpc_getnextexten(Type, Ext)
			else:
				log.msg('no need to recheck, its final' + Ext)
				return Ext
		except:
			return 0000
			
	def xmlrpc_getchanstatus(self):
		ech = os.popen("/usr/sbin/asterisk  -rx 'core show channels concise'")
		output = ech.read()
		output = output.strip()
		output = output.split('\n')
		arr = []
		for line in output:
			sline = line.split('!')
			arr.append(sline)
		return arr


	def xmlrpc_hangup(self, Channel):
		log.msg(Channel)
		ech = os.popen("/usr/sbin/asterisk  -rx 'soft hangup "+Channel+"'")
		log.msg("/usr/sbin/asterisk  -rx 'soft hangup "+Channel+"'")
		return 1

	def xmlrpc_checkextension(self, Exten,Skip=None):
		ListExtens = self.xmlrpc_getdp('all')
		log.msg('check exten: arg->' +Exten)
		for EExten in ListExtens:
			log.msg(EExten)
			if EExten[0] == Exten:
				return Exten
			else:
				pass
		return 0

	def xmlrpc_stopservice(self):
		response,regexcode,exitcode = self.command("stopasterisk")
		return (exitcode == 0)


	def xmlrpc_startservice(self):
		response,regexcode,exitcode = self.command("startasterisk")
		return (exitcode == 0)


	def reload(self):
		ps = os.popen(CMD_PATH + "zasterisk")
		return 1
