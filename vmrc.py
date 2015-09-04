#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# VMware vSphere Python SDK
# Copyright (c) 2008-2013 VMware, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#pip install setproctitle
#pip install pyvmomi

#MODIFIED FOR VMRC PURPOSES



#Enter either your vcenter or your esxi server here
host = "192.168.1.1"

""" Python program for listing the vms on an ESX / vCenter host """

import atexit
import sys


if sys.version_info[0] < 3:
    print("Please use Python 3!!")
    sys.exit(0)

def installfrompip(package):
    import pip
    pip.main(['install', package])

try:
    from pyVim import connect
    from pyVmomi import vmodl
except ImportError:
     answer = input("pyvmomi not installed.  Do you want to run the installation command now [pip3 install pyvmomi](Y/n)?")
     if answer == 'N' or answer == 'n':
         print("Quitting!")
     else:
         installfrompip('pyvmomi')


from distutils.spawn import find_executable
import os
import os.path
import subprocess
import getpass
from collections import OrderedDict
import re

#import tools.cli as cli
#DISABLE SSL CERT VERIFICATION
from pyVim.connect import SmartConnect
import requests
requests.packages.urllib3.disable_warnings()
import ssl
#ssl.SSLContext.verify_mode = ssl.CERT_NONE
ssl._create_default_https_context = ssl._create_unverified_context
vmdict = {}
ctr = 0
depthctr = 0
depthmax = 10
user = ""
pwd = ""


def resetvars():
    global vmdict
    global depthctr
    global ctr
    vmdict.clear()
    depthctr = 0
    ctr = 0

def get_vm_path(virtual_machine, depth=1):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection.

    :param virtual_machine:
    :param depth:
    """
    maxdepth = 10

    # if this is a group it will have children. if it does, recurse into them
    # and then return
    if hasattr(virtual_machine, 'childEntity'):
        if depth > maxdepth:
            return
        #vmList = virtual_machine.childEntity
        #for c in vmList:
        #    print(c, depth + 1)
        #return

    summary = virtual_machine.summary
    return summary.config.vmPathName
    #print("Name       : ", summary.config.name)
    #print("Path       : ", summary.config.vmPathName)
    #print("Guest      : ", summary.config.guestFullName)
    #print("Instance UUID : ", summary.config.instanceUuid)
    #print("Bios UUID     : ", summary.config.uuid)
    #annotation = summary.config.annotation
    #if annotation:
    #    print("Annotation : ", annotation)
    #print("State      : ", summary.runtime.powerState)
    #if summary.guest is not None:
    #    ip_address = summary.guest.ipAddress
    #    if ip_address:
    #        print("IP         : ", ip_address)
    #if summary.runtime.question is not None:
    #    print("Question  : ", summary.runtime.question.text)
    #print ("HOST : ", summary.runtime.host.summary.config.name)
    #print("")


def add_vm_name(virtual_machine, depth=1):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection.

    :param virtual_machine:
    :param depth:
    """
    maxdepth = 50

    # if this is a group it will have children. if it does, recurse into them
    # and then return
    if hasattr(virtual_machine, 'childEntity'):
        if depth > maxdepth:
            return
        #vmList = virtual_machine.childEntity
        #for c in vmList:
        #    print(c, depth + 1)
        #return
    
    if hasattr(virtual_machine, 'summary'):
        summary = virtual_machine.summary
        #print("Name       : ", summary.config.name)
        vmdict[virtual_machine] = summary.config.name


def vmconsole(path, host):
    """

    :param path:
    :param host:
    :param username:
    :param password:
    """
    executable = find_executable("vmplayer")
    if not executable:
        print(
            "VMware Player not installed! Download here: https://my.vmware.com/web/vmware/free#desktop_end_user_computing/vmware_player/7_0")
        exit()
    #print(vmplayerargs)
    esxusr = input("Enter ESXi username for " + host + ":")
    #esxpwd = getpass.getpass("Enter ESXi password: ")
    vmplayerargs = " -U " + esxusr + " -H " + host + " \"" + path + "\""
    subprocess.call('nohup ' + executable + vmplayerargs + ' &', shell=True)
    #subprocess.setproctitle("VMware Player")

def vmcollect(datacenter):
        global depthctr
        global depthmax
        if depthmax == depthctr:
            print("Max depth reached: " + str(depthmax))
            return
        #print ("Descending into: " + str(datacenter.name))
        if hasattr(datacenter, 'vmFolder'):
            #for dcchild in datacenter:
            dcchild = datacenter
            vm_folder = dcchild.vmFolder
            vm_list = vm_folder.childEntity
            #print("vm list:  " + str(vm_list))
        else:
            vm_folder = datacenter
            vm_list = vm_folder.childEntity
            #print (vm_list)
        for virtual_machine in vm_list:
            if hasattr(virtual_machine, 'childType'):
                print("VM Group: " + virtual_machine.name)
                depthctr += 1
                vmcollect(virtual_machine)
                continue
            else:
                add_vm_name(virtual_machine, 10)

def main():
    global ctr
    global user
    global pwd
    global vmdict
    global host
    """ Simple command-line program for listing the virtual machines on a system. """
    executable = find_executable("vmplayer")
    if not executable:
        print(
            "VMware Player not installed! Download here: https://my.vmware.com/web/vmware/free#desktop_end_user_computing/vmware_player/7_0")
        exit()
    #args = cli.get_args()
    if not user:
        user = input("Enter vcenter username: ")
    if not pwd:
    	pwd = getpass.getpass("Enter vcenter password: ")
    port = "443"
    
    try:
        print("Trying Connection...")
        service_instance = connect.SmartConnect(host=host,
                                            user=user,
                                            pwd=pwd,
                                            port=int(port))

        atexit.register(connect.Disconnect, service_instance)
        print("Connected...")

        content = service_instance.RetrieveContent()
        children = content.rootFolder.childEntity
        for child in children:
            if hasattr(child, 'vmFolder'):
                datacenter = child
                vmcollect(datacenter)
            else:
                # some other non-datacenter type object
                print ("Other: " + child)
                continue
                #print (virtual_machine)
        sortedvms = []
        #Let's take the numbers from the dictionary and append them to the name
        for vmname in vmdict:
            sortedvms.append(vmname.summary.config.name + " : " + str(ctr))
            ctr += 1
        sortedvms = sorted(sortedvms)
        for vmname in sortedvms:
            #Let's pull back out the number from the dictionary
            splitstr = re.search('(.*)(?:\s:\s)(\d*$)', vmname)
            number = splitstr.group(2)
            if (len(splitstr.group(2)) == 1):
                number = splitstr.group(2) + " "
            print(number + " : " + splitstr.group(1))
        #print (service_instance)
        #print (vmarray)
        choosenum = int(input("Choose a number: "))
        selectvm = list(vmdict)[choosenum]
        ##Python 2 specific code
        #if vmdict.keys()[choosenum]:
        #    print (vmdict.keys()[choosenum])
        print(selectvm.summary.config.vmPathName)
        #selectvmpath=getvmpath(selectvm, 10)
        vmconsole(selectvm.summary.config.vmPathName,
                  selectvm.summary.runtime.host.summary.config.name)
        resetvars()
        main()
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1
        #pass
    else:
        print("Huh?")

    return 0

# Start program
if __name__ == "__main__":
    main()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
