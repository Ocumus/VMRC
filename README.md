# VMRC

This project is a python3 based wrapper that allows a user to easily start VMware Remote Console sessions through VMware Player on Linux.

It will connect to a vCenter server and get a list of all of the VMs available.  After which it will ask you to select the correct number
of the VM you wish to connect to.  It will then spawn a VMware Player session to the Host that the VM is currently sitting on.

# Background  

There is no longer support for NPAPI in Google Chrome, so the standard VMRC stopped working on Linux.  VMware does not have a good solution thus far and they are working on a standalone version for Linux.  Until then, this script should do the trick.
http://kb.vmware.com/selfservice/microsites/search.do?language=en_US&cmd=displayKC&externalId=2091284

The vCenter In-browser Web Console for Linux sucks and doesn't pass through a lot of keyboard commands.  With VMware Player on Linux, the connection acts just like a VMRC connection within Windows where you press Ctrl+Alt to get out of the VM and all other keyboard/mouse commands are sent to the VM.

The issue with VMware Player on Linux is that you must enter the ESX host you want to connect to as well as the path to the VMX file to get to VM.  Entering this information is quite cumbersome unless you put it in a script.  Even then, you will have issues if your VMs move from host to host or switch datastores.

This script queries vCenter for all of that information and connects to the correct host and to the correct path for the VMX file. 

# Configuration Options

Host - This parameter should be set to either your vCenter server if you have one or to your ESXi server if you don't.

verifysslcert - Set this option to False if you do not want to verify your SSL certificate.  This is not recommended.


#Requirements

Python3

VMware Player for Linux https://www.vmware.com/products/player

pyvmomi package

pip - if you want auto-installation of needed packages

Currently tested on Ubuntu, but should work on other distros.


# Caveats

This script cannot re-use your vCenter/ESX password that you enter initially to login into a VMRC session.  You will just have to enter it again once VMware Player starts.
This is caused by the fact that VMware Player does not sanitize the password string if it is passed through the commandline which leaves your password
visible to anyone who can see the command you ran with ps.

You will be logging in directly to an ESX server even if you have vCenter when spawning a VMRC session. Your credentials will need to be valid directly on
each ESX server, or you will need to use a local account on the ESX server.
