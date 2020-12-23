#!/bin/bash
# UPS Plus installation script.

# initializing init-functions.
. /lib/lsb/init-functions

# check if the network is working properly.
log_action_msg "Start the configuration environment check..."
ping_result=`ping -c 4 www.github.com &> /dev/null` 
if [[ $ping_result -ne 0 ]]; then
	log_warning_msg "Network is not available!"
	log_warning_msg "Please check the network configuration and try again!"
else
	log_action_msg "Network status is ok..."
fi

# Package check and installation
install_pkgs()
{
	`sudo apt-get update -qq`
	`sudo apt -y -qq install git`
}

log_action_msg "Start the software check..."
pkgs=`dpkg -l | awk '{print $2}' | egrep ^git$`
if [[ $pkgs = 'git' ]]; then
	log_action_msg "Git Package has been installed alreay."
else
	log_action_msg "Installing git package..."
	install_pkgs
	if [[ $? -eq 0 ]]; then 
	   log_action_msg "Package installation successfully."
	else
	   log_warning_msg "Package installation is failed,please install git package manually or check the repository"
	fi
fi	

# TODO: check python libararies and installation.
# TODO: Create daemon service or crontab by creating python scripts. 

