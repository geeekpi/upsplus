#!/bin/bash
# uninstall shell script
. /lib/lsb/init-functions

# Remove crontab 
log_action_msg "Remove crontab for $USER"
sudo sed -i '/upsPlus/d' /var/spool/cron/crontabs/pi
cron_result=`grep -i upsplus /var/spool/cron/crontabs/pi |wc -l`
if [[ $cron_result -gt 0 ]]; then
	log_failure_msg "Can not remove crontab for $USER, please do it manually."
else
	log_success_msg "Crontab for $USER has been removed."
fi
# Remove $HOME/bin/upsPlus*
rm -f $HOME/bin/upsPlus*
if [[ $? -eq 0 ]]; then
	log_success_msg "Remove $HOME/bin/upsPlus.* successful."
else
	log_failure_msg "Can not remove $HOME/bin/upsPlus.*, please remove it manully."
fi
# TODO: Greetings
log_success_msg "52Pi UPS Plus python script has been removed successful"
log_action_msg "------------------More Information---------------------"
log_action_msg "https://wiki.52pi.com/index.php/UPS_Plus_SKU:_EP-0136"
log_action_msg "----------------Thanks from 52Pi Team------------------"
