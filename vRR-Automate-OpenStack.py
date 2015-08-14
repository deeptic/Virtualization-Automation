"""
Autor : Deepti Chandra

Objective : This script aims at building VRR topologies on KVM using OpenStack

Version   : 1 [Cleanup pending] Furture versions would be more dynamic

"""

#!/usr/bin/env python

############################### VARIABLE DECLARATIONS ###############################  

global serverIp

global login

global instanceName

global instanceType

global numInstances

global instanceType 

global numInstanceNics

global instanceNicNetwork 

global instanceNicSubnet

global keystoneAuthPort




global True 

global False 

global logTitle

global logExtnsn



global sshNewkey


global prompt

global session

global callInstNetCreate





############################### VARIABLE DEFINITIONS ###############################

logTitle          = "Log_VRR_OpenStackCLI"

logExtnsn         = '.txt'

keystoneAuthPort  = '5000'

numInstanceNics   = 2


sshNewkey         = 'Are you sure you want to continue connecting'

prompt            = '.*@.*\$'

callInstNetCreate = 0




############################### FUNCTION DEFINITIONS ###############################

#DEFINING A MAIN()

def Main():

	import sys
    
	sshServer, pwd, getInstanceData, osAdminUser, osAdminPasswd, osAdminTenant, osAuthUrl, vrrimageLocation, pubNwName, pubSubnetName, pubSubnet, pubPoolStart, pubPoolEnd, pubGw   =   Initialize()

	TopologyLayout (getInstanceData)


	logFile                 =   CreateLogFile()

	session                 =   LoginServer(logFile, sshServer, pwd)


	adminCredentials        =   AuthAdmin(logFile, session, osAdminUser, osAdminPasswd, osAdminTenant, osAuthUrl)

	CreateTenant     (logFile, session, adminCredentials, 'Guest-Topology' ,'Tenant for Guest')

	guestCredentials        =   CreateTenantUser (logFile, session, adminCredentials, 'Guest-Topology' ,'guest-user', 'guest', osAuthUrl)
	

	RegisterVRRImage  (logFile, session, adminCredentials, guestCredentials, 'vRR-image', vrrimageLocation)

	CreateVRRFlavor   (logFile, session, 'Guest-Topology' , adminCredentials, guestCredentials, 'vRR-flavor', '16384' , '10' , '1')

	CreatePublicNw    (logFile, session, 'Guest-Topology' , adminCredentials, guestCredentials, pubNwName, pubSubnetName, pubSubnet, pubPoolStart, pubPoolEnd, pubGw)
		
	CreateInstance    (logFile, session, 'Guest-Topology' , adminCredentials, guestCredentials, getInstanceData)

	UpInstance        (logFile, session, 'Guest-Topology' , adminCredentials, guestCredentials, getInstanceData, 'vRR-image', 'vRR-flavor') 
		
	CreateRouter      (logFile, session, 'Guest-Topology' , adminCredentials, guestCredentials, getInstanceData, 'GWR') 

	SetGW             (logFile, session, 'Guest-Topology' , adminCredentials, guestCredentials, 'GWR', pubNwName) 

	AssignFloatingIP  (logFile, session, 'Guest-Topology' , adminCredentials, guestCredentials, getInstanceData, 'GWR', pubNwName, pubPoolStart)

	SecGroupRules     (logFile, session, 'Guest-Topology' , adminCredentials, guestCredentials, 'default') 






		
class InstanceData():
    "Stores data needed to create an instance"
    def __init__(self, instName, instType, totInst, totNics, nicNum, nicNet, nicSubnet, nicSubnetIP):
        self.instName    = instName
        self.instType    = instType
        self.totInst     = totInst
        self.totNics     = totNics
        self.nicNum      = nicNum
        self.nicNet      = nicNet
        self.nicSubnet   = nicSubnet
        self.nicSubnetIP = nicSubnetIP








def Initialize():

	import sys

	
	print "\n"
	print "\t\t\t" + "*" * 89
	print "\t\t\t**********  VRR Topology Instantiation using OpenStack Command-Line-Interface  ********** "
	print "\t\t\t" + "*" * 89


	print "\n\n"

	print ("\t\t\t" + "-" * 27 + '  Parameter Initialization Summary  ' + "-" * 27 )
	print "\t\t\t" + "-" * 90


	print "\n\n\t\t\t Please enter information for the parameters requested below : "


	serverIp         =  raw_input("\n" + "\t" * 4 + " Enter Host Server IP                                :     ")
	login            =  raw_input("\n" + "\t" * 4 + " Enter Host Server Username                          :     ")
	pwd              =  raw_input("\n" + "\t" * 4 + " Enter Host Server Password                          :     ")
	sshServer        =  login + '@' + serverIp
	vrrimageLocation =  raw_input("\n" + "\t" * 4 + " Enter (local)location of vRR Junos image            :     ")
   

	pubNwName        =  raw_input("\n" + "\t" * 4 + " Enter name of public network                        :     ") 
	pubSubnetName    =  raw_input("\n" + "\t" * 4 + " Enter name of public subnet for public network      :     ")
	pubSubnet        =  raw_input("\n" + "\t" * 4 + " Enter IP/mask of public subnet for public network   :     ")
	pubPoolStart     =  raw_input("\n" + "\t" * 4 + " Enter start IP for public pool allocation           :     ")
	pubPoolEnd       =  raw_input("\n" + "\t" * 4 + " Enter end IP for public pool allocation             :     ")
	pubGw            =  raw_input("\n" + "\t" * 4 + " Enter IP of public gateway                          :     ")



	osAdminUser      =  raw_input("\n" + "\t" * 4 + " Enter username for user with 'admin' role           :     ")
	osAdminPasswd    =  raw_input("\n" + "\t" * 4 + " Enter password for user with 'admin' role           :     ")
	osAdminTenant    =  raw_input("\n" + "\t" * 4 + " Enter tenant-name for user with 'admin' role        :     ")
	
    #http://docs.openstack.org/developer/keystone/configuration.html
	osAuthUrl        =  'http://' + serverIp + ':' + keystoneAuthPort + '/v2.0/'
	osAuthUrlOK      =  raw_input("\n" + "\t" * 4 + " Is URL %s ? [yes/no]  :      " %osAuthUrl)
	if (osAuthUrlOK == "no") :
		osAuthUrl    =  raw_input("\n" + "\t" * 4 + " Enter keystone authentication URL                  	 :     ")
	elif (osAuthUrlOK == "yes") :
		print("\n" + "\t" * 4 + " Keystone authentication URL confirmed               :     %s" %osAuthUrl)						
	else :
		sys.exit("\n" + "\t" * 4 + " Invalid choice - Need authentication URL !  Terminating ...\n")		


	getInstanceData = []	


	numInstances   =  raw_input("\n" + "\t" * 4 + " Enter total number of VRR instances to spawn        :     ")
    

	if (numInstances == "0") :
		sys.exit("\n" + "\t" * 4 + " No instances to be spawned !  Terminating ...\n")
	
	else :	
	
		for instance in range (int(numInstances)) :
			instance+=1
			print ("\n" + "\t" * 5 + " For instance %d  :" %instance) 
			print "\t" * 5 + "-" * 16
			
			instanceName  = raw_input("\t" * 6 + " Enter Instance Name                 :     ")

			
			
			instanceType  = raw_input("\t" * 6 + " Enter Instance Type [ VRR | VMX ]   :     ")
			if ((instanceType != "VRR") and (instanceType != "VMX")):
				sys.exit("\t" * 6 + " Invalid instance type !  Terminating ...\n")




			instanceNics  = raw_input("\t" * 6 + " Enter number of NICs for instance   :     ")	
			
			if (int(instanceNics) > numInstanceNics) :
				sys.exit("\t" * 6 + " Invalid number of NICs (Currently only %d supported) !  Terminating ...\n" %numInstanceNics)
			
			for nic in range (int(instanceNics)) :
				nic+=1
				print ("\t" * 6 + " For NIC %d :" %nic) 
				instanceNicNetwork    = raw_input("\t" * 7 + " Enter name of network to be assigned to this NIC   :     ")
				instanceNicSubnet     = raw_input("\t" * 7 + " Enter name of subnet to be assigned to this NIC    :     ")
				instanceNicSubnetIP   = raw_input("\t" * 7 + " Enter subnet IP/mask to be assigned to this NIC    :     ")

			
				getInstanceData.append(InstanceData(instanceName, instanceType, numInstances, instanceNics, nic, instanceNicNetwork, instanceNicSubnet, instanceNicSubnetIP))


	
	print "\n\n"

	print "\t\t\t" + "-" * 102

	return (sshServer, pwd, getInstanceData, osAdminUser, osAdminPasswd, osAdminTenant, osAuthUrl, vrrimageLocation, pubNwName, pubSubnetName, pubSubnet, pubPoolStart, pubPoolEnd, pubGw)				










def TopologyLayout (getInstanceData) : 
	
	from prettytable import PrettyTable
	
	print "\n\n\n"
	print ("\t\t\t" + "-" * 27 + '  Initiating creation of VRR baseline topology  ' + "-" * 27 )
	print "\t\t\t" + "-" * 102

	print "\n\n" + "===> Data for instances to be created : " + "\n"
	

	tbl = PrettyTable(["Instance Name", "Instance Type", "Total Instances", "Total NICs" , "Instance NIC #", "NIC Network", "NIC Subnet", "NIC Subnet IP/mask"])
	
	tbl.align["Instance Name"] = "c" 
	
	tbl.padding_width = 1 
	

	instanceDataLen = len(getInstanceData)
	
	for element in range (instanceDataLen) :
		tbl.add_row([getInstanceData[element].instName, getInstanceData[element].instType, getInstanceData[element].totInst, getInstanceData[element].totNics, getInstanceData[element].nicNum, getInstanceData[element].nicNet, getInstanceData[element].nicSubnet, getInstanceData[element].nicSubnetIP])
		
	
	print tbl	










def CreateLogFile() :

	import datetime

	now     = datetime.datetime.now()

	logFile = "%s_%.2i-%.2i-%i_%.2i-%.2i-%.2i" % (logTitle,now.day,now.month,now.year,now.hour,now.minute,now.second)
	
	logFile = logFile + logExtnsn

	print "\n\n" + "===> Session captures in log file = ",logFile

	return logFile









def LoginServer(logFile, sshServer, pwd) :

		import pexpect

		import re

		global session

		session=pexpect.spawn("ssh %s" %sshServer)

		session.logfile= open(logFile, "w")

		chkKey=session.expect([sshNewkey,'password:',pexpect.EOF,pexpect.TIMEOUT],90) #0 if no key, 1 if has key
	
		if chkKey==0 :

				print "\n\n" + "===> Server not known - Adding ssh key"

				session.sendline("yes")

				chkKey=session.expect([sshNewkey,'password:',pexpect.EOF])


		if chkKey==1:
				
				print "\n\n" + "===> Server ssh key known - Proceeding with password authentication"
					
				session.sendline("%s" %pwd)

				session.sendline("\r")
	
				return session	

		elif chkKey==2:

			print "\n\n" + "===> Connection timeout"

			pass











def AuthAdmin(logFile, session, osAdminUser, osAdminPasswd, osAdminTenant, osAuthUrl):

	import pexpect

	print "\n\n\t\t *** Step 1 =>  Composing 'admin' user credentials ***"
	
	import sys

	import time




	session.timeout=250


	fout = file (logFile, "w")

	session.logfile= open(logFile, "w")

	session.logfile=fout


	adminAuthCmds=['export admin_credentials="--os-username %s --os-password %s --os-tenant-name %s --os-auth-url %s"' %(osAdminUser, osAdminPasswd, osAdminTenant, osAuthUrl),'echo $admin_credentials','date']
	

	for element in adminAuthCmds:

		session.sendline("\r")

		session.expect("%s \r" %prompt)

		session.sendline("\r")

		session.sendline("%s \r" %element)

		session.expect("%s \r" %prompt)

		session.sendline("\r")

		
	adminCredentials = '--os-username ' +  osAdminUser +' --os-password ' + osAdminPasswd + ' --os-tenant-name ' + osAdminTenant + ' --os-auth-url ' + osAuthUrl		

	return adminCredentials

	#! TO ADD CODE FOR ERROR DETECTION & THEN PRINT THIS 	












def CreateTenant (logFile, session, adminCredentials, tenantName , tenantDesc):

	import pexpect

	import re

	import time

	session.timeout=250

	
	fout = file (logFile, "w")

	session.logfile= open(logFile, "w")

	session.logfile=fout



	print "\n\n\t\t *** Step 2 =>  Creating tenant for guest topology ***"



	createTenantCmds=["keystone %s tenant-list" %adminCredentials, 
	    			  "keystone %s tenant-create --name %s --description '%s' " %(adminCredentials, tenantName, tenantDesc),
		              "keystone %s tenant-list" %adminCredentials, 'date', 
		              "keystone %s tenant-list" %adminCredentials, 'date']

	
		


	for element in createTenantCmds:

		session.sendline("\r")

		session.expect("%s \r" %prompt)

		session.sendline("\r")

		session.sendline("%s \r" %element)

		session.sendline("\r")

		time.sleep(5) 	

	#! TO ADD CODE FOR ERROR DETECTION 
	print "\t\t\t    >>> Creation of guest tenant %s successful (without 'admin' role) !" %tenantName	
	











def CreateTenantUser (logFile, session, adminCredentials, tenantName, tenantUser , tenantPwd, osAuthUrl):

	import pexpect

	import re

	import time

	session.timeout=250

	
	fout = file (logFile, "w")

	session.logfile= open(logFile, "w")

	session.logfile=fout



	print "\n\n\t\t *** Step 3 =>  Creating tenant user for guest topology tenant ***"


	
	createUserCmds=["keystone %s user-list" %adminCredentials,
					"export tenant_id=$(keystone %s tenant-list | grep %s | awk ' {print $2} ')" %(adminCredentials, tenantName),
					"echo $tenant_id",
					"keystone %s user-create --name %s --tenant_id=$tenant_id --pass %s " %(adminCredentials, tenantUser,tenantPwd),
					"keystone %s user-list" %adminCredentials, 'date', 
					'export guest_credentials="--os-username %s --os-password %s --os-tenant-name %s --os-auth-url %s"' %(tenantUser, tenantPwd, tenantName, osAuthUrl),
					'echo $guest_credentials','date']

					
	for element in createUserCmds:

		session.sendline("\r")

		session.expect("%s \r" %prompt)

		session.sendline("\r")

		session.sendline("%s \r" %element)

		session.sendline("\r")

		time.sleep(5) 		
	

	guestCredentials = '--os-username ' +  tenantUser +' --os-password ' + tenantPwd + ' --os-tenant-name ' + tenantName + ' --os-auth-url ' + osAuthUrl		


	#! TO ADD CODE FOR ERROR DETECTION & THEN PRINT THIS 	
	print "\t\t\t    >>> Creation of guest tenant user %s successful !" %tenantUser	
	print "\t\t\t        Credentials for guest tenant user in tenant %s : Username - %s , Password - %s" %(tenantName, tenantUser, tenantPwd)	
		

	return guestCredentials










def RegisterVRRImage (logFile, session, adminCredentials, guestCredentials, imageName, vrrimageLocation):

	import pexpect

	import re

	import time

	session.timeout=250

	
	fout = file (logFile, "w")

	session.logfile= open(logFile, "w")

	session.logfile=fout



	print "\n\n\t\t *** Step 4 =>  Register vRR Junos image for guest topology tenant ***"


	registerVrrImageCmds=["glance %s image-list" %adminCredentials, 
					  	  "glance %s image-list" %guestCredentials, 
	    			      "glance %s image-create --name %s --disk-format=qcow2 --container-format=bare --file=%s --owner $tenant_id" %(adminCredentials, imageName, vrrimageLocation),
		              	  "glance %s image-list" %adminCredentials, 
					  	  "glance %s image-list" %guestCredentials,
					  	  "glance %s image-update --property hw_disk_bus=ide --property hw_cdrom_bus=ide --property hw_vif_model=e1000  %s" %(guestCredentials, imageName),
		              	  "glance %s image-list" %adminCredentials, 'date', 
		              	  "glance %s image-list" %guestCredentials, 'date']

	
		


	for element in registerVrrImageCmds:

		session.sendline("\r")

		session.expect("%s \r" %prompt)

		session.sendline("\r")

		session.sendline("%s \r" %element)

		session.sendline("\r")

		time.sleep(5) 	

	#! TO ADD CODE FOR ERROR DETECTION 
	print "\t\t\t    >>> Registration of vRR image for guest tenant successful (can be used if user desires to create vRR VMs)!" 











def CreateVRRFlavor (logFile, session, tenantName, adminCredentials, guestCredentials, flavorName, vrrRam, vrrDisk, vrrVcpus):

	import pexpect

	import re

	import time

	session.timeout=250

	
	fout = file (logFile, "w")

	session.logfile= open(logFile, "w")

	session.logfile=fout



	print "\n\n\t\t *** Step 5 =>  Create vRR flavor(private) for guest topology tenant ***"


	createVrrFlavorCmds=["export flavor_id=$(nova %s flavor-list | tail -2 | awk ' {print $2} ')" %guestCredentials,
						 "echo $flavor_id",
						 "export new_flavor_id=$flavor_id",
						 "echo $new_flavor_id",
						 "export new_flavor_id=$((flavor_id+1))",
						 "echo $new_flavor_id",
						 "nova %s flavor-list" %guestCredentials,
						 "nova %s flavor-list" %adminCredentials,
						 "nova $admin_credentials flavor-create --is-public false %s $new_flavor_id %s %s %s" %(flavorName, vrrRam, vrrDisk, vrrVcpus),
						 "keystone %s tenant-list" %adminCredentials,
						 "export tenant_id=$(keystone %s tenant-list | grep %s | awk ' {print $2} ')" %(adminCredentials, tenantName),
						 "echo $tenant_id",
						 "nova %s flavor-access-add %s $tenant_id" %(adminCredentials, flavorName),
						 "nova %s flavor-list" %guestCredentials,
						 "nova %s flavor-list" %adminCredentials,
						 "nova %s flavor-list" %guestCredentials,
						 "nova %s flavor-list" %adminCredentials,
						 'date']

	
		


	for element in createVrrFlavorCmds:

		session.sendline("\r")

		session.expect("%s \r" %prompt)

		session.sendline("\r")

		session.sendline("%s \r" %element)

		session.sendline("\r")

		time.sleep(5) 	

	#! TO ADD CODE FOR ERROR DETECTION 
	print "\t\t\t    >>> Creation of vRR flavor for guest tenant successful (can be used if user desires to create vRR VMs)!" 










def CreatePublicNw (logFile, session, tenantName, adminCredentials, guestCredentials, pubNwName, pubSubnetName, pubSubnet, pubPoolStart, pubPoolEnd, pubGw):

	import pexpect

	import re

	import time

	session.timeout=250

	
	fout = file (logFile, "w")

	session.logfile= open(logFile, "w")

	session.logfile=fout

	print "\n\n\t\t *** Step 6 =>  Create public network for guest topology tenant ***"


	createPubNwCmds=["neutron %s net-create %s --router:external=True --tenant-id $tenant_id" %(adminCredentials,pubNwName),
					 "export tenant_id=$(keystone %s tenant-list | grep '%s' | awk ' {print $2} ')" %(adminCredentials, tenantName),
					 "echo $tenant_id",
					 "neutron %s subnet-create %s %s --name %s --enable_dhcp=False --allocation-pool start=%s,end=%s --gateway=%s --tenant-id $tenant_id" %(adminCredentials,pubNwName, pubSubnet, pubSubnetName, pubPoolStart, pubPoolEnd, pubGw),
					 "neutron %s net-list" %guestCredentials,
					 "neutron %s subnet-list" %guestCredentials,
					 "neutron %s net-external-list" %guestCredentials,
					 "neutron %s net-list" %adminCredentials,
					 "neutron %s subnet-list" %adminCredentials,
					 "neutron %s net-external-list" %adminCredentials,
					 "neutron %s net-list" %guestCredentials,
					 "neutron %s subnet-list" %guestCredentials,
					 "neutron %s net-external-list" %guestCredentials,
					 "neutron %s net-list" %adminCredentials,
					 "neutron %s subnet-list" %adminCredentials,
					 "neutron %s net-external-list" %adminCredentials,
					 'date']

	
		


	for element in createPubNwCmds:

		session.sendline("\r")

		session.expect("%s \r" %prompt)

		session.sendline("\r")

		session.sendline("%s \r" %element)

		session.sendline("\r")

		time.sleep(5) 	

	#! TO ADD CODE FOR ERROR DETECTION 
	print "\t\t\t    >>> Creation of public network for guest tenant successful (can be used if user desires to create vRR VMs)!" 











def CreateInstance   (logFile, session, tenantName , adminCredentials, guestCredentials, getInstanceData) :
	
	import pexpect

	import re

	import time

	session.timeout=250

	global callInstNetCreate



	instanceDataLen = len(getInstanceData)

	print "\n\n\t\t *** Step 7  =>  Instance Network/Subnet Creation  ***" 
	
	
	nicNetList = []
	for element in range (instanceDataLen) :
		nicNetList.append(getInstanceData[element].nicNet)
		
	

	for element in range (instanceDataLen) :

		print "\n\t\t\t     =>  Instance                 -    %s " %getInstanceData[element].instName
		print "\t\t\t     =>  Create network/subnet    -    NIC : %s , NIC network : %s ,  NIC subnet : %s , NIC subnet IP/mask : %s" %(getInstanceData[element].nicNum, getInstanceData[element].nicNet, getInstanceData[element].nicSubnet, getInstanceData[element].nicSubnetIP)
		
		uniqueNet = nicNetList.count(getInstanceData[element].nicNet)
		print "\t\t\t     >>> Multiple instances have requested to create network : %s !" %(getInstanceData[element].nicNet)
		


		if ((uniqueNet > 1) and (callInstNetCreate == 0)) :
			callInstNetCreate += 1
			netDoneInstName = getInstanceData[element].instName
			netDoneInstNet  = getInstanceData[element].nicNet
			CreateInstanceNetwork (logFile, session, tenantName , adminCredentials, guestCredentials, getInstanceData[element].instName, getInstanceData[element].nicNum, getInstanceData[element].nicNet, getInstanceData[element].nicSubnet, getInstanceData[element].nicSubnetIP)
			
		
		
		if ((uniqueNet > 1) and (callInstNetCreate != 0) and (netDoneInstNet  != getInstanceData[element].nicNet)) :
			if (netDoneInstName == getInstanceData[element].instName) :
				callInstNetCreate += 1

				netDoneInstName = getInstanceData[element].instName
				netDoneInstNet  = getInstanceData[element].nicNet

				CreateInstanceNetwork (logFile, session, tenantName , adminCredentials, guestCredentials, getInstanceData[element].instName, getInstanceData[element].nicNum, getInstanceData[element].nicNet, getInstanceData[element].nicSubnet, getInstanceData[element].nicSubnetIP)
				





		


def CreateInstanceNetwork   (logFile, session, tenantName , adminCredentials, guestCredentials, instanceName, instanceNicNum, instanceNicNet, instanceNicSubnet,  instanceNicSubnetIP) :
	
	import pexpect

	import re

	import time

	session.timeout=250


	
	fout = file (logFile, "w")

	session.logfile= open(logFile, "w")

	session.logfile=fout

	
	createInstNwCmds=["neutron %s net-list" %guestCredentials,
					  "neutron %s subnet-list" %guestCredentials,	
					  "neutron %s net-list" %adminCredentials,
					  "neutron %s subnet-list" %adminCredentials,
					  "export tenant_id=$(keystone %s tenant-list | grep '%s' | awk ' {print $2} ')" %(adminCredentials, tenantName),
					  "echo $tenant_id",
					  "neutron %s net-create %s " %(guestCredentials, instanceNicNet),
					  "neutron %s subnet-create --name %s %s %s " %(guestCredentials, instanceNicSubnet, instanceNicNet, instanceNicSubnetIP),
					  "neutron %s net-list" %guestCredentials,
					  "neutron %s subnet-list" %guestCredentials,	
					  "neutron %s net-list" %adminCredentials,
					  "neutron %s subnet-list" %adminCredentials,
					  "neutron %s net-list" %guestCredentials,
					  "neutron %s subnet-list" %guestCredentials,
					  'date']

	
		


	for element in createInstNwCmds:

		session.sendline("\r")

		session.expect("%s \r" %prompt)

		session.sendline("\r")

		session.sendline("%s \r" %element)

		session.sendline("\r")

		time.sleep(10) 	

	#! TO ADD CODE FOR ERROR DETECTION 
	print "\t\t\t     >>> For instance %s       -   Creation of network %s & subnet %s - %s for guest tenant successful !" %(instanceName, instanceNicNet, instanceNicSubnet,  instanceNicSubnetIP)



	






def UpInstance   (logFile, session, tenantName , adminCredentials, guestCredentials, getInstanceData, imageName, flavorName) :  
	
	import pexpect

	import re

	import time

	session.timeout=250

	print "\n\n\t\t *** Step 8  =>  Boot Instances  ***" 

	
	instanceDataLen = len(getInstanceData)




	instNameList = []
	for element in range (instanceDataLen) :
		instNameList.append(getInstanceData[element].instName)


	instanceNameLen = len(instNameList)

	GetInstanceNetID(logFile, session, tenantName , adminCredentials, guestCredentials, getInstanceData, imageName, flavorName)










def GetInstanceNetID(logFile, session, tenantName , adminCredentials, guestCredentials, getInstanceData, imageName, flavorName) : 

	import pexpect

	import re

	import time

	session.timeout=250


	
	fout = file (logFile, "w")

	session.logfile= open(logFile, "w")

	session.logfile=fout



	instanceDataLen = len(getInstanceData)

	

	instNameList = []
	for element in range (instanceDataLen) :
			instNameList.append(getInstanceData[element].instName)
	instanceNameLen  = len(instNameList)

	uniqinstNameSet      = set(instNameList)
	uniqinstNameList     = list(uniqinstNameSet)
	uniqinstanceNameLen  = len(uniqinstNameList)
	start = 0 


	#Get flavor id
	getInstFlavorIDCmds=["nova %s flavor-list" %guestCredentials,
						 "vrrFlavorID=$(nova %s flavor-list | grep '%s' | tail -2 | awk ' {print $2} ')" %(guestCredentials, flavorName),
						 "echo $vrrFlavorID", 
						 'date']

	for cmd in getInstFlavorIDCmds :

		session.sendline("\r")

		session.expect("%s \r" %prompt)

		session.sendline("\r")

		session.sendline("%s \r" %cmd)

		session.sendline("\r")

		time.sleep(10)	




	#Get NIC ID 
	nicstrList = []


	for element in range (instanceDataLen) :
		prev = element - 1
		next = element + 1 

		
		
		if (element == 0) : 
			getInstNicIDCmds=["neutron %s net-list" %guestCredentials,
					     	  "vrrNet%sID=$(neutron %s net-list | grep '%s' |cut -c3-39)" %(getInstanceData[element].nicNum, guestCredentials, getInstanceData[element].nicNet),
						  	  "echo $vrrNet%sID" %getInstanceData[element].nicNum, 
						      'date']


			nicstrList.append("vrrNet%sID"%getInstanceData[element].nicNum)
			#print "%s" %nicstrList			      

			for cmd in getInstNicIDCmds:

				session.sendline("\r")

				session.expect("%s \r" %prompt)

				session.sendline("\r")

				session.sendline("%s \r" %cmd)

				session.sendline("\r")

				time.sleep(10)


			
			
			if (getInstanceData[element].nicNum == int(getInstanceData[element].totNics)) :
					nicStr = ' --nic ' + ' --nic '.join(nicstrList)

					bootInstCmds=["nova %s boot --image %s --flavor $vrrFlavorID %s '%s' " %(guestCredentials, imageName, nicStr, getInstanceData[element].instName), 
								  "nova %s list " %guestCredentials, "nova %s list " %adminCredentials,
								  'date']

					for cmd in bootInstCmds:

						session.sendline("\r")

						session.expect("%s \r" %prompt)

						session.sendline("\r")

						session.sendline("%s \r" %cmd)

						session.sendline("\r")

						time.sleep(30)	


					nicstrList[:] = []
					nicStr = ''

		


		if 	(element > 0) :
			
			if (getInstanceData[element].instName == getInstanceData[prev].instName) :
				
				getInstNicIDCmds=["neutron %s net-list" %guestCredentials,
					     	      "vrrNet%sID=$(neutron %s net-list | grep '%s' |cut -c3-39)" %(getInstanceData[element].nicNum, guestCredentials, getInstanceData[element].nicNet),
						  	      "echo $vrrNet%sID" %getInstanceData[element].nicNum, 
						          'date']


				nicstrList.append("vrrNet%sID"%getInstanceData[element].nicNum)
				#print "%s" %nicstrList			      

				for cmd in getInstNicIDCmds:

					session.sendline("\r")

					session.expect("%s \r" %prompt)

					session.sendline("\r")

					session.sendline("%s \r" %cmd)

					session.sendline("\r")

					time.sleep(10)



				if (getInstanceData[element].nicNum == int(getInstanceData[element].totNics)) :
					
					nicStr = ' --nic net-id=$' + ' --nic net-id=$'.join(nicstrList)

					bootInstCmds=["nova %s boot --image %s --flavor $vrrFlavorID %s '%s' " %(guestCredentials, imageName, nicStr, getInstanceData[element].instName), 
								  "nova %s list " %guestCredentials, "nova %s list " %adminCredentials,
								  'date']

					for cmd in bootInstCmds:

						session.sendline("\r")

						session.expect("%s \r" %prompt)

						session.sendline("\r")

						session.sendline("%s \r" %cmd)

						session.sendline("\r")

						time.sleep(30)			  

					nicstrList[:] = []
					nicStr = ''


			if (getInstanceData[element].instName != getInstanceData[prev].instName) :
					
				getInstNicIDCmds=["neutron %s net-list" %guestCredentials,
					     	      "vrrNet%sID=$(neutron %s net-list | grep '%s' |cut -c3-39)" %(getInstanceData[element].nicNum, guestCredentials, getInstanceData[element].nicNet),
						  	      "echo $vrrNet%sID" %getInstanceData[element].nicNum, 
						          'date']


				nicstrList.append("vrrNet%sID"%getInstanceData[element].nicNum)
					      

				for cmd in getInstNicIDCmds:

					session.sendline("\r")

					session.expect("%s \r" %prompt)

					session.sendline("\r")

					session.sendline("%s \r" %cmd)

					session.sendline("\r")

					time.sleep(10)



				if (getInstanceData[element].nicNum == int(getInstanceData[element].totNics)) :
					
					nicStr = ' --nic net-id=$' + ' --nic net-id=$'.join(nicstrList) 
					
					bootInstCmds=["nova %s boot --image %s --flavor $vrrFlavorID %s '%s' " %(guestCredentials, imageName, nicStr, getInstanceData[element].instName), 
								  "nova %s list " %guestCredentials, "nova %s list " %adminCredentials,
								  'date']

					for cmd in bootInstCmds:

						session.sendline("\r")

						session.expect("%s \r" %prompt)

						session.sendline("\r")

						session.sendline("%s \r" %cmd)

						session.sendline("\r")

						time.sleep(30)	



					nicstrList[:] = []
					nicStr = ''
					




def CreateRouter  (logFile, session, tenantName , adminCredentials, guestCredentials, getInstanceData, routerName) :  

	import pexpect

	import re

	import time

	session.timeout=250


	
	fout = file (logFile, "w")

	session.logfile= open(logFile, "w")

	session.logfile=fout
	

	print "\n\n\t\t *** Step 9 =>  Create router for guest topology tenant ***"


	createRtrCmds=["neutron %s router-list" %guestCredentials,
				   "neutron %s router-create '%s' " %(guestCredentials, routerName),
				   "neutron %s router-list" %guestCredentials,
				   "routerID=$(neutron %s router-list | grep '%s' | cut -c3-39)" %(guestCredentials, routerName),
				   "echo $routerID",
				   "neutron %s router-list" %guestCredentials,
				   "neutron %s router-list" %adminCredentials,
				   'date']

	
		


	for element in createRtrCmds:

		session.sendline("\r")

		session.expect("%s \r" %prompt)

		session.sendline("\r")

		session.sendline("%s \r" %element)

		session.sendline("\r")

		time.sleep(15) 	





	instanceDataLen = len(getInstanceData)

	nicNetList = []
	for element in range (instanceDataLen) :
		nicNetList.append(getInstanceData[element].nicNet)
		


	for element in range (instanceDataLen) :

		subID = element + 1

		createRtrPortCmds=["neutron %s subnet-list" %guestCredentials,
					 	   "subnet%sID=$(neutron %s subnet-list| grep '%s' | cut -c3-39)" %(subID, guestCredentials, getInstanceData[element].nicSubnet),
					 	   "echo $subnet%sID" %subID,
					 	   "routerID=$(neutron %s router-list | grep '%s' | cut -c3-39)" %(guestCredentials, routerName),
					 	   "echo $routerID",
					 	   "neutron %s router-interface-add $routerID $subnet%sID" %(guestCredentials, subID),
					 	   "neutron %s router-port-list %s" %(guestCredentials, routerName),
					 	   "neutron %s router-port-list %s" %(guestCredentials, routerName),
					 	   'date']
		
		for element in createRtrPortCmds:

			session.sendline("\r")

			session.expect("%s \r" %prompt)

			session.sendline("\r")

			session.sendline("%s \r" %element)

			session.sendline("\r")

			time.sleep(15) 					 	   

	

	#! TO ADD CODE FOR ERROR DETECTION 
	print "\t\t\t    >>> Creation of router and ports for guest tenant successful !" 












def SetGW  (logFile, session, tenantName , adminCredentials, guestCredentials, routerName, pubNwName) :  

	import pexpect

	import re

	import time

	session.timeout=250


	
	fout = file (logFile, "w")

	session.logfile= open(logFile, "w")

	session.logfile=fout
	

	print "\n\n\t\t *** Step 10 =>  Set created router to be external-gateway for guest topology tenant ***"



	setGWCmds=["neutron %s router-list" %guestCredentials,
			   "routerID=$(neutron %s router-list | grep '%s' | cut -c3-39)" %(guestCredentials, routerName),
			   "echo $routerID",
			   "publicNwID=$(neutron %s net-list | grep '%s' | cut -c3-39)" %(guestCredentials, pubNwName),
			   "echo $publicNwID",
			   "neutron %s router-gateway-set $routerID $publicNwID" %guestCredentials,
			   "neutron %s router-list" %adminCredentials,
			   "neutron %s router-list" %guestCredentials,
			   'date']

	
		


	for element in setGWCmds:

		session.sendline("\r")

		session.expect("%s \r" %prompt)

		session.sendline("\r")

		session.sendline("%s \r" %element)

		session.sendline("\r")

		time.sleep(15) 	



	#! TO ADD CODE FOR ERROR DETECTION 
	print "\t\t\t     >>> Setting created router to external-gateway for guest tenant successful !" 









def AssignFloatingIP  (logFile, session, tenantName , adminCredentials, guestCredentials, getInstanceData, routerName, pubNwName, pubPoolStart) :  

	import pexpect

	import re

	import time

	from netaddr import *

	import pprint

	session.timeout=250


	
	fout = file (logFile, "w")

	session.logfile= open(logFile, "w")

	session.logfile=fout
	

	print "\n\n\t\t *** Step 11 =>  Assign floating IPs for guest topology tenant ***"


	createFloatNwCmds=["neutron %s floatingip-list" %guestCredentials,
				   "neutron %s floatingip-list" %adminCredentials,
				   "neutron %s floatingip-create '%s' " %(guestCredentials, pubNwName),
				   "neutron %s floatingip-list" %guestCredentials,
				   "neutron %s floatingip-list" %adminCredentials,
				   'date']

	
		


	for element in createFloatNwCmds:

		session.sendline("\r")

		session.expect("%s \r" %prompt)

		session.sendline("\r")

		session.sendline("%s \r" %element)

		session.sendline("\r")

		time.sleep(15) 	



	

	instanceDataLen = len(getInstanceData)


	#GET UNIQUE INSTANCE NAMES
	instNameList = []
	for element in range (instanceDataLen) :
		instNameList.append(getInstanceData[element].instName)


	uniqueInstName    =  list(set(instNameList))
	uniqueInstNameLen =  len(uniqueInstName)

	print "\t\t\t     >>> Assuming a contiguous pool of floating IPs for guest tenant !" 
	print "\t\t\t     >>> Floating IP assigned to the router =  %s  for guest tenant successful !" %pubPoolStart

	

	for element in range (uniqueInstNameLen) :

		incr  		= element + 1
		ip          = IPAddress(pubPoolStart)
		intIP 		= int(ip)
		assignintIP = intIP + incr
		assignIP    = IPAddress(assignintIP)

		assignFloatIPCmds=["nova %s floating-ip-associate '%s' %s" %(guestCredentials,uniqueInstName[element], assignIP), 
						   "neutron %s floatingip-list" %guestCredentials,
						   "nova %s floating-ip-list" %guestCredentials,
						   "neutron %s floatingip-list" %adminCredentials,
						   "nova %s floating-ip-list" %adminCredentials,
				   		   'date']


		
		for element in assignFloatIPCmds :

			session.sendline("\r")

			session.expect("%s \r" %prompt)

			session.sendline("\r")

			session.sendline("%s \r" %element)

			session.sendline("\r")

			time.sleep(15) 

		
		print "\t\t\t     >>> Floating IP assigned to the Instance %s =  %s  for guest tenant successful !" %(uniqueInstName[incr - 1],assignIP)						 	   

	

	#! TO ADD CODE FOR ERROR DETECTION 
	print "\t\t\t     >>> Floating IP assignment to all devices for guest tenant successful !" 












def SecGroupRules  (logFile, session, tenantName , adminCredentials, guestCredentials, grpName) :  

	import pexpect

	import re

	import time


	session.timeout=250


	
	fout = file (logFile, "w")

	session.logfile= open(logFile, "w")

	session.logfile=fout
	

	print "\n\n\t\t *** Step 12 =>  Add security group rules in group '%s' for guest topology tenant ***" %grpName


	addSecGrpRulesCmds=[ "neutron %s security-group-rule-list" %guestCredentials,
						 "neutron %s security-group-rule-list" %adminCredentials,
				   		 "nova %s secgroup-add-rule default tcp  22 22 0.0.0.0/0" %guestCredentials,
				   		 "nova %s secgroup-add-rule default icmp -1 -1 0.0.0.0/0" %guestCredentials,
				   		 "neutron %s security-group-rule-list" %guestCredentials,
						 "neutron %s security-group-rule-list" %adminCredentials,
				   		 'date']

	
		


	for element in addSecGrpRulesCmds:

		session.sendline("\r")

		session.expect("%s \r" %prompt)

		session.sendline("\r")

		session.sendline("%s \r" %element)

		session.sendline("\r")

		time.sleep(15) 	


	
	#! TO ADD CODE FOR ERROR DETECTION 
	print "\t\t\t     >>>  Addition of security group rules for guest tenant successful !" 	









Main()	








