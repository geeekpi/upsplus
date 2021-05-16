#!/bin/bash
# uninstall shell script
. /lib/lsb/init-functions

# Remove crontab 
log_action_msg "Remove crontab "
crontab -l | grep -v 'upsPlus' | crontab -
cron_result=$(crontab -l | grep -c -i 'upsPlus')
if [[ $cron_result -gt 0 ]]; then
	log_failure_msg "Can not remove crontab, please do it manually."
else
	log_success_msg "Crontab for upsPlus has been removed."
fi
# Remove $HOME/bin/upsPlus*

if ! rm -f "$HOME"/bin/upsPlus*; then
	log_failure_msg "Can not remove $HOME/bin/upsPlus.*, please remove it manully."
else
	log_success_msg "Remove $HOME/bin/upsPlus.* successful."
fi
# TODO: Greetings
log_success_msg "52Pi UPS Plus python script has been removed successful"
log_action_msg "------------------More Information---------------------"
log_action_msg "https://wiki.52pi.com/index.php/UPS_Plus_SKU:_EP-0136"
log_action_msg "----------------Thanks from 52Pi Team------------------"
