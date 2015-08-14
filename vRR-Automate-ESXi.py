"""
Author    : Deepti Chandra

Objective : This script aims at building a static topology [including hybridging with an option for configuring Junos] on the ESXi infrasturucture

Version   : 1 [Cleanup pending] Furture versions would be more dynamic

  +-------+
  |       |
  |       |
  |       |                                           +---------------+
  |       |       +---------------+                   |  VRR-2 [.248] |
  |       |       |      MX-1     |                   |               |
  |       |       |               |    172.25.213     |               |
  |     2/2-------1/0/2        2/0/0-------------------em3.1 [eth 10] |
  |       |       |               |.150            .151               |
  |       |       |               |                   |               |
  |       |       |      tab      |                   +---------------+
  |       |       +---------------+
  |       |
  |       |
  |       |
  |       |
  |  RT   |
  |davinci|
  |       |
  |       |
  |       |        +---------------+                  +---------------+
  |       |        |      MX-2     |                  |  VRR-1 [.247] |
  |       |        |               |                  |               |
  |       |        |               |    172.25.214    |               |
  |     1/13-------2/1/3        2/0/0------------------em3.1 [eth 11] |
  |       |        |               .155             .154              |
  |       |        |    sterbai    |                  |               |
  |       |        +---------------+                  +---------------+
  |       |
  |       |
  |       |
  |       |
  |       |
  |       |
  +-------+
"""

#!/usr/bin/env python



global serverIp

global login

global pwd

global logTitle

global sshNewkey

global sshServer

global session

global esxiDefaultPrompt

global esxiPrompt

global mgtUl

global VRR1toMX1Ul

global VRR1toMX2Ul 

global VRR2toMX1Ul

global VRR2toMX2Ul

global logFile

global vRROnly 

global vRRConf

global basePath

global baseVmdk

global vRR1Vmdk

global vRR2Vmdk

global vM1

global vM2

global basevRR1Vmx

global basevRR2Vmx

global vRR1Vmx

global vRR2Vmx

global baseConf

global vRR1Conf

global vRR2Conf

global dummyMgtIP

global confPwd

global vMDefaultPrompt

global vMConfigPrompt

global vRR1Conffile 

global vRR2Conffile 



vM1 = 'vRR1'

vM2 = 'vRR2'

vRROnly = "1"

vRRConf = "2"

serverIp = "192.168.182.166" 

dummyMgtIP = "192.168.182.247"

login = "root" 

pwd = "Embe1mpls"

confPwd = "MaRtInI"

confUser = "regress"

vMDefaultPrompt = confUser + '@VRR>'

vMConfigPrompt = confUser + '@VRR#'

logTitle = "VRR-topology-bringup"

logExtnsn = '.log'

sshNewkey = 'Are you sure you want to continue connecting'

sshServer = login + '@' + serverIp

esxiDefaultPrompt = '~ #'

esxiPrompt = '#'

mgtUl = 'vmnic12'

VRR1toMX1Ul = 'vmnic4'

VRR1toMX2Ul = 'vmnic3'

VRR2toMX1Ul = 'vmnic5'

VRR2toMX2Ul = 'vmnic2'

basePath = '/vmfs/volumes/datastore1/'

baseVmdk = basePath + 'BASE-VMDK/base-vmdk.vmdk'

baseConf = basePath + 'BASE-CONFIG/'

vRR1Vmdk = '/vmfs/volumes/datastore1/'+ vM1 + '/' + vM1 +'.vmdk'

vRR2Vmdk = '/vmfs/volumes/datastore1/'+ vM2 + '/' + vM2 +'.vmdk'

basevRR1Vmx  = '/vmfs/volumes/datastore1/BASE-VMDK/'+ vM1 +'.vmx'

basevRR2Vmx  = '/vmfs/volumes/datastore1/BASE-VMDK/'+ vM2 +'.vmx'

vRR1Vmx	= '/vmfs/volumes/datastore1/'+ vM1 + '/' + vM1 +'.vmx'

vRR2Vmx = '/vmfs/volumes/datastore1/'+ vM2 + '/' + vM2 +'.vmx'

vRR1Conf = baseConf + 'VRR1-config.conf'

vRR2Conf = baseConf + 'VRR2-config.conf'

vRR1Conffile = 'VRR1-config.conf'

vRR2Conffile = 'VRR2-config.conf'



def UserPref():

	import sys

	selection = raw_input("Enter :\n[1] To create only the VM topology \n[2] To load the Junos baseline config after creating the VM topology\nSelect : ")

	#selection.rstrip()

	print "You entered : ",selection



	if ((selection != "1") and (selection != "2")):

		print "\nInvalid selection : ",selection

		print "For valid choices type either 1 or 2"

	

	if (selection == "1"):

		proceed = raw_input("\nProceeding to create the VRR baseline topology WITHOUT loading Junos config. Do you wish to continue [yes/no] ? ")

		if (proceed != "yes"):

			sys.exit("Terminating ...\n")

		if (proceed == "yes"):

			#return "1"

			return vRROnly





	if (selection == "2"):

		proceed = raw_input("\nProceeding to create the VRR baseline topology WITH loading Junos config. Do you wish to continue [yes/no] ? ")

		if (proceed != "yes"):

			sys.exit("Terminating ...\n")

		if (proceed == "yes"):

			#return "2"

			return vRRConf

	

		



def CreateLogFile():

	import datetime

	now = datetime.datetime.now() 

	logFile = "%s_%.2i-%.2i-%i_%.2i-%.2i-%.2i" % (logTitle,now.day,now.month,now.year,now.hour,now.minute,now.second)

	logFile = logFile + logExtnsn

	print "\t => Session captures in log file = ",logFile

	return logFile











def LoginServer(logFile):

		import pexpect

		global session

		session=pexpect.spawn("ssh %s" %sshServer)

		session.logfile= open(logFile, "w")

		chkKey=session.expect([sshNewkey,'Password:',pexpect.EOF,pexpect.TIMEOUT],90) #0 if no key, 1 if has key

		if chkKey==0 :

				print "\n\t => ESXi Server not known - Adding ssh key"

				session.sendline("yes")

				chkKey=session.expect([sshNewkey,'Password:',pexpect.EOF])

		if chkKey==1:

				print "\n\t => ESXi Server ssh key known - Proceeding with password authentication"

				session.sendline("%s" %pwd)

				session.expect("%s" %esxiPrompt)

				return session

				

		elif chkKey==2:

			print "\n\t => Connection timeout"

			pass

	









def CloneBase(session):

		import pexpect

		print "\t\t Step 1 => Cloning Base Image to create VRR1 & VRR2 VMDK files"

		session.timeout=250

		vmBaseClone=['pwd','cd %s' %basePath,'mkdir %s' %vM1,'mkdir %s' %vM2,'vmkfstools -i %s %s' %(baseVmdk,vRR1Vmdk),'vmkfstools -i %s %s' %(baseVmdk,vRR2Vmdk), 'ls -lrt','ls -lrt %s' %vM1,'ls -lrt %s' %vM2]		

		

		for element in vmBaseClone:

			session.sendline("\r")

			session.expect("%s \r" %esxiPrompt)

			session.sendline("\r")

			session.sendline("%s \r" %element)

			session.sendline("\r")

		







def CreateVswitch(session):

		import pexpect

		print "\t\t Step 2 => Creating vSwitches for hybridging"

		session.timeout=250

		

		vSwitchStatus=['esxcli network vswitch standard list','esxcli network ip interface list','esxcli network nic list']



		for set1 in vSwitchStatus:

			session.sendline("\r")

			session.expect("%s \r" %esxiPrompt)

			session.sendline("\r")

			session.sendline("%s \r" %set1)

			session.sendline("\r")







		#By default, the ESXi, the management vmkernel port is vmk0 and resides in a Standard Switch portgroup called Management Network.

		#http://kb.vmware.com/selfservice/microsites/search.do?language=en_US&cmd=displayKC&externalId=1008127

		#No management switch or port-group created - Default one created for esxi is used, only uplink mapped,port-group to map VRR em0 used in vmx file



		

		vSwitchMgt=['esxcli network vswitch standard uplink add --uplink-name=%s --vswitch-name=vSwitch0' %mgtUl]

	

		#for set2 in vSwitchMgt:

			#print ("%s \r" %set2)

			#session.sendline("\r")

			#session.expect("%s \r" %esxiPrompt)

			#session.sendline("\r")

			#session.sendline("%s \r" %set2)

			#session.sendline("\r")





		vSwitchCreate=['esxcli network vswitch standard add --vswitch-name=vswitch1','esxcli network vswitch standard portgroup add --portgroup-name=Internal-VRR --vswitch-name=vswitch1','esxcli network vswitch standard add --vswitch-name=vSwitch2','esxcli network vswitch standard portgroup add --portgroup-name="VRR1 - MX1" --vswitch-name=vSwitch2','esxcli network vswitch standard uplink add --uplink-name=%s --vswitch-name=vSwitch2' %VRR1toMX1Ul,'esxcli network vswitch standard add --vswitch-name=vSwitch3','esxcli network vswitch standard portgroup add --portgroup-name="VRR1 - MX2" --vswitch-name=vSwitch3','esxcli network vswitch standard uplink add --uplink-name=%s --vswitch-name=vSwitch3' %VRR1toMX2Ul,'esxcli network vswitch standard add --vswitch-name=vSwitch4','esxcli network vswitch standard portgroup add --portgroup-name="VRR2 - MX1" --vswitch-name=vSwitch4','esxcli network vswitch standard uplink add --uplink-name=%s --vswitch-name=vSwitch4' %VRR2toMX1Ul,'esxcli network vswitch standard add --vswitch-name=vSwitch5','esxcli network vswitch standard portgroup add --portgroup-name="VRR2 - MX2" --vswitch-name=vSwitch5','esxcli network vswitch standard uplink add --uplink-name=%s --vswitch-name=vSwitch5' %VRR2toMX2Ul]



		for set3 in vSwitchCreate:

			session.sendline("\r")

			session.expect("%s \r" %esxiPrompt)

			session.sendline("\r")

			session.sendline("%s \r" %set3)

			session.sendline("\r")

	







		vSwitchStatus=['esxcli network vswitch standard list','esxcli network ip interface list','esxcli network nic list']



		for set1 in vSwitchStatus:

			session.sendline("\r")

			session.expect("%s \r" %esxiPrompt)

			session.sendline("\r")

			session.sendline("%s \r" %set1)

			session.sendline("\r")





		

		





def GetVMXfile(session):

		import pexpect

		print "\t\t Step 3 => Creating .vmx files for creating VMs"

		session.timeout=250



		vmxFiles=['cp %s %s'%(basevRR1Vmx,vRR1Vmx),'cp %s %s' %(basevRR2Vmx,vRR2Vmx),'ls -lrt %s' %vM1,'ls -lrt %s' %vM2]



		for element in vmxFiles:

			session.sendline("\r")

			session.expect("%s \r" %esxiPrompt)

			session.sendline("\r")

			session.sendline("%s \r" %element)

			session.sendline("\r")



		







def RegisterVM(session):

		import pexpect

		print "\t\t Step 4 => Register VMs to complete VM creation"

		session.timeout=250



		vmRegister=['vim-cmd vmsvc/getallvms','vim-cmd solo/registervm %s' %vRR1Vmx,'vim-cmd solo/registervm %s' %vRR2Vmx,'vim-cmd vmsvc/getallvms']



		for element in vmRegister:

			session.sendline("\r")

			session.expect("%s \r" %esxiPrompt)

			session.sendline("\r")

			session.sendline("%s \r" %element)

			session.sendline("\r")





	







def GetVMID(session):

		import pexpect

		import re

		

		print "\t\t Step 5 => Check for VM IDs to see if VM creation is successful"

		session.timeout=250



		vmGetID=['vim-cmd vmsvc/getallvms | grep vRR1', 'vim-cmd vmsvc/getallvms | grep vRR2']



		for element in vmGetID:

			session.sendline("\r")

			session.expect("%s \r" %esxiPrompt)

			session.sendline("\r")

			session.sendline("%s \r" %element)

			session.sendline("\r")

			



		session.expect("%s" %esxiPrompt)

		session.sendline('exit')

		session.expect(pexpect.EOF)

		#print session.before # print out the result



		handle = open ("%s" %logFile,"r")



		

		matchVRR1 = r'(.*)vRR1(.*)freebsd64Guest(.*)'

		matchVRR2 = r'(.*)vRR2(.*)freebsd64Guest(.*)'



		for line in handle:

			if re.match(matchVRR1,line):

				print "\t\t\t vRR1 created successfully =>  ", line

				vrr1ID = line.split(' ')

				break



		for line in handle:

			if re.match(matchVRR2,line):

				print "\t\t\t vRR2 created successfully =>  ", line

				vrr2ID = line.split(' ')

				break



		return vrr1ID[0],vrr2ID[0]



		





			





def PowerVMs(session,vrr1ID,vrr2ID):

		import pexpect

		import re

		import sys

		

		print "\t\t Step 6 => Power on created VMs"

		session.timeout=250





		vmPower=['vim-cmd vmsvc/power.on %s' %vrr1ID, 'vim-cmd vmsvc/power.on %s' %vrr2ID, 'vim-cmd vmsvc/power.getstate %s' %vrr1ID, 'vim-cmd vmsvc/power.getstate %s' %vrr2ID, ]



		for element in vmPower:

			session.sendline("\r")

			session.expect("%s \r" %esxiPrompt)

			session.sendline("\r")

			session.sendline("%s \r" %element)

			session.sendline("\r")





		session.expect("%s" %esxiPrompt)

		session.sendline('exit')

		session.expect(pexpect.EOF)





		matchPowerVRR1 = r'%s(.*)power.getstate %s' %(esxiDefaultPrompt,vrr1ID)

		matchPowerVRR2 = r'%s(.*)power.getstate %s' %(esxiDefaultPrompt,vrr2ID)



		data = [line.strip() for line in open("%s" %logFile, 'r')]

		



		for i in range(len(data)):

			if re.match(matchPowerVRR1,data[i]):

				if re.match(r'Powered(.*)',data[i + 2]):

					print "\t\t\t  vRR1 ID = %s , State =  %s " %(vrr1ID, data[i + 2])

					statevRR1 = data[i + 2]

					if re.match(r'Powered on',statevRR1):

						print "\t\t\t  vRR1 has been powered on successfully !"

					else:

						print "\t\t\t  vRR1 has could not be powered on. Manual intervention required."

						sys.exit("Terminating ...\n")





		for i in range(len(data)):

			if re.match(matchPowerVRR2,data[i]):

				if re.match(r'Powered(.*)',data[i + 2]):

					print "\t\t\t  vRR2 ID = %s , State =  %s " %(vrr2ID, data[i + 2])

					statevRR2 = data[i + 2]

					if re.match(r'Powered on',statevRR2):

						print "\t\t\t  vRR2 has been powered on successfully !"

					else:

						print "\t\t\t  vRR2 has could not be powered on. Manual intervention required."

						sys.exit("Terminating ...\n")

		

		

		







def PowerVM(session,vM,vrrID):

		import pexpect

		import re

		import sys

		

		print "\t\t === > FOR %s <===" %vM

		print "\t\t Step 6 => Power on created VMs"

		session.timeout=250





		vmPower=['vim-cmd vmsvc/power.on %s' %vrrID,'vim-cmd vmsvc/power.getstate %s' %vrrID]



		for element in vmPower:

			session.sendline("\r")

			session.expect("%s \r" %esxiPrompt)

			session.sendline("\r")

			session.sendline("%s \r" %element)

			session.sendline("\r")





		session.expect("%s" %esxiPrompt)

		session.sendline('exit')

		session.expect(pexpect.EOF)





		matchPowerVRR = r'%s(.*)power.getstate %s' %(esxiDefaultPrompt,vrrID)



		data = [line.strip() for line in open("%s" %logFile, 'r')]

		



		for i in range(len(data)):

			if re.match(matchPowerVRR,data[i]):

				if re.match(r'Powered(.*)',data[i + 2]):

					print "\t\t\t vRR = %s , vRR ID = %s , State =  %s " %(vM,vrrID, data[i + 2])

					statevRR = data[i + 2]

					if re.match(r'Powered on',statevRR):

						print "\t\t\t  %s has been powered on successfully !" %vM

					else:

						print "\t\t\t  %s has could not be powered on. Manual intervention required." %vM

						sys.exit("Terminating ...\n")











def OffVM(session,vM,vrrID):

		import pexpect

		import re

		import sys

		

		print "\t\t Step 10 => Power off created VMs"

		session.timeout=250





		vmPower=['vim-cmd vmsvc/power.off %s' %vrrID,'vim-cmd vmsvc/power.getstate %s' %vrrID]



		for element in vmPower:

			session.sendline("\r")

			session.expect("%s \r" %esxiPrompt)

			session.sendline("\r")

			session.sendline("%s \r" %element)

			session.sendline("\r")





		session.expect("%s" %esxiPrompt)

		session.sendline('exit')

		session.expect(pexpect.EOF)





		matchPowerVRR = r'%s(.*)power.getstate %s' %(esxiDefaultPrompt,vrrID)



		data = [line.strip() for line in open("%s" %logFile, 'r')]

		



		for i in range(len(data)):

			if re.match(matchPowerVRR,data[i]):

				if re.match(r'Powered(.*)',data[i + 2]):

					print "\t\t\t vRR = %s , vRR ID = %s , State =  %s " %(vM,vrrID, data[i + 2])

					statevRR = data[i + 2]

					if re.match(r'Powered off',statevRR):

						print "\t\t\t  %s has been powered off successfully !" %vM

					else:

						print "\t\t\t  %s has could not be powered off. Manual intervention required." %vM

						sys.exit("Terminating ...\n")



		



def PingMgt(session,vM,dummyMgtIP):

		import pexpect

		import re

		import sys

		import time



		print "\t\t Step 7 => Check if dummy management IP reachable on powered on VMs - %s" %vM

		session.timeout=250



		vmPing=['ping %s -c 3' %dummyMgtIP,"date"]



	

		for count in range(0, 5):

			for element in vmPing:

				session.sendline("\r")

				session.expect("%s \r" %esxiPrompt)

				session.sendline("\r")

				session.sendline("%s \r" %element)

				session.sendline("\r")

				time.sleep(70)

				

		session.expect("%s" %esxiPrompt)

		session.sendline('exit')

		session.expect(pexpect.EOF)





		matchPing = r'%s ping %s -c 3' %(esxiDefaultPrompt,dummyMgtIP)

		matchUp   = r'(.*)0% packet loss'



		data = [line.strip() for line in open("%s" %logFile, 'r')]

		

		last = len(data) - 1



		for i in range(len(data)):

			if re.match(matchUp,data[i]):	

				print "\t\t\t %s is up now. Pings to the dummy management IP %s work => %s " %(vM,dummyMgtIP,data[i])

				break













def CopyConf(session,vM,dummyMgtIP,vRRConf):

		import pexpect

	

		print "\t\t Step 8 => Copy Junos Baseline config to created VMs - %s" %vM

		session.timeout=250



		session.sendline("\r")

		session.expect("%s \r" %esxiPrompt)

		session.sendline("\r")

		session.sendline('scp -p %s %s@%s:/var/tmp/' %(vRRConf,confUser,dummyMgtIP))



		chkKey=session.expect([sshNewkey,'Password:',pexpect.EOF,pexpect.TIMEOUT],90) #0 if no key, 1 if has key

		if chkKey==0 :

				print "\n\t => Ssh key not known for scp - Adding ssh key"

				session.sendline("yes")

				chkKey=session.expect([sshNewkey,'Password:',pexpect.EOF])

		if chkKey==1:

				print "\n\t => Ssh key known for scp - Proceeding with password authentication"

				session.sendline("%s" %confPwd)

				session.expect("%s" %esxiPrompt)

				

		elif chkKey==2:

			print "\n\t => Connection timeout"

			pass



		print "\t\t\t %s has been copied over to %s successfully ! " %(vRRConf,vM)







	





def LoadConf(session,vM,dummyMgtIP,vRRConffile):

		import pexpect

	

		print "\t\t Step 9 => Load Junos Baseline config %s to created VRRs - %s" %(vRRConffile,vM)

		session.timeout=250



		session.sendline("\r")

		session.expect("%s \r" %esxiPrompt)

		session.sendline("\r")

		session.sendline('ssh %s@%s' %(confUser,dummyMgtIP))

		session.expect('Password:')

		session.sendline("%s" %confPwd)	

		session.sendline("\r")

		session.expect("%s \r" %vMDefaultPrompt)

		session.sendline("\r")



		session.sendline("\r")

		session.expect("%s \r" %vMDefaultPrompt)

		session.sendline("edit \r")

		session.expect("%s \r" %vMConfigPrompt)

		session.sendline("\r")

		session.expect("%s \r" %vMConfigPrompt)

		session.sendline("load override /var/tmp/%s\r" %vRRConffile)

		session.expect("%s \r" %vMConfigPrompt)

		session.sendline("\r")

		session.expect("%s \r" %vMConfigPrompt)

		session.sendline("commit and-quit\r")

		

		print "\t\t\t %s has been loaded on %s successfully ! " %(vRRConffile,vM)



		session = LoginServer(logFile)

		

		





	









#Script will either just automate the VM operations OR automate the VM operations and copy the config file to the routers as well

#Ask the user for preference



scrRun = UserPref()



if (scrRun == vRROnly):

	print "\n ***** Initiating creation of VRR baseline topology  ***** \n"

	logFile = CreateLogFile()

	session = LoginServer(logFile)

	CloneBase(session)

	CreateVswitch(session)

	GetVMXfile(session)

	RegisterVM(session)

	vrr1ID,vrr2ID = GetVMID(session)

	session = LoginServer(logFile)

	PowerVMs(session,vrr1ID,vrr2ID)

	print "\n ***** Creation of VRR baseline topology completed ***** \n"





if (scrRun == vRRConf):

	print "\n ***** Initiating creation of baseline VRR topology with Junos configuration  ***** \n"

	logFile = CreateLogFile()

	session = LoginServer(logFile)

	CloneBase(session)

	CreateVswitch(session)

	GetVMXfile(session)

	RegisterVM(session)

	vrr1ID,vrr2ID = GetVMID(session)

	

	session = LoginServer(logFile)

	PowerVM(session,vM1,vrr1ID)

	session = LoginServer(logFile)

	PingMgt(session,vM1,dummyMgtIP)	

	session = LoginServer(logFile)

	CopyConf(session,vM1,dummyMgtIP,vRR1Conf)

	session = LoginServer(logFile)

	LoadConf(session,vM1,dummyMgtIP,vRR1Conffile)

	session = LoginServer(logFile)	

	OffVM(session,vM1,vrr1ID)



	session = LoginServer(logFile)

	PowerVM(session,vM2,vrr2ID)

	session = LoginServer(logFile)

	PingMgt(session,vM2,dummyMgtIP)	

	session = LoginServer(logFile)

	CopyConf(session,vM2,dummyMgtIP,vRR2Conf)

	session = LoginServer(logFile)

	LoadConf(session,vM2,dummyMgtIP,vRR2Conffile)

	session = LoginServer(logFile)	

	OffVM(session,vM2,vrr2ID)



	session = LoginServer(logFile)

	PowerVM(session,vM1,vrr1ID)

	session = LoginServer(logFile)

	PowerVM(session,vM2,vrr2ID)

			

	print "\n ***** Creation of baseline VRR topology with Junos configuration  completed ***** \n"



       

		

		

main ()	
