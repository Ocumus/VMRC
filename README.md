# VMRC

This project is a python3 based wrapper that allows a user to easily start VMware Remote Console sessions through VMware Player on Linux.

# Configuration Options

Host - This parameter should be set to either your vCenter server if you have one or to your ESXi server if you don't.


#Requirements

Python3

pip - if you want auto-installation of needed packages

pyvmomi package

Currently tested on Ubuntu, but should work on other distros.


# Caveats

This script cannot re-use your vCenter/ESX password that you enter initially to login into a VMRC session.  You will just have to enter it again.
This is caused by the fact that VMware Player does not sanitize the password string if it is passed through the commandline which leaves your password
visible to anyone who can see the command you ran with ps.

You will be logging in directly to an ESX server even if you have vCenter when spawning a VMRC shell. Your credentials will need to be valid directly on
each ESX server, or you will need to use a local account on the ESX server.
