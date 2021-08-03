#!/bin/bash
# UPS Plus installation script.

# initializing init-functions.
. /lib/lsb/init-functions
sudo raspi-config nonint do_i2c 0

# check if the network is working properly.
log_action_msg "Welcome to 52Pi Technology UPS Plus auto-install Program!"
log_action_msg "More information please visit here:"
log_action_msg "-----------------------------------------------------"
log_action_msg "https://wiki.52pi.com/index.php/UPS_Plus_SKU:_EP-0136"
log_action_msg "-----------------------------------------------------"
log_action_msg "Start the configuration environment check..."
ping_result=`ping -c 4 www.github.com &> /dev/null` 
if [[ $ping_result -ne 0 ]]; then
	log_failure_msg "Network is not available!"
	log_warning_msg "Please check the network configuration and try again!"
else
	log_success_msg "Network status is ok..."
fi

# Package check and installation
install_pkgs()
{
	`sudo apt-get -qq update`
	`sudo apt-get -y -qq install sudo git i2c-tools`
}

log_action_msg "Start the software check..."
pkgs=`dpkg -l | awk '{print $2}' | egrep ^git$`
if [[ $pkgs = 'git' ]]; then
	log_success_msg "git has been installed."
else
	log_action_msg "Installing git package..."
	install_pkgs
	if [[ $? -eq 0 ]]; then 
	   log_success_msg "Package installation successfully."
	else
	   log_failure_msg "Package installation is failed,please install git package manually or check the repository"
	fi
fi	

# install pi-ina219 library.
ina_pkg=`pip3 list | grep ina |awk '{print $1}'`
if [[ $ina_pkg = 'pi-ina219' ]]; then
	log_success_msg "pi-ina219 library has been installed"
else
	log_action_msg "Installing pi-ina219 library..."
	pip3 install pi-ina219
	if [[ $? -eq 0 ]]; then
	   log_success_msg "pi-ina219 Installation successful."
	else
	   log_failure_msg "pi-ina219 installation failed!"
	   log_warning_msg "Please install it by manual: pip3 install pi-ina219"
	fi
fi
# install smbus2 library.
log_action_msg "Installing smbus2 library..."
pip3 install smbus smbus2
if [[ $? -eq 0 ]]; then
        log_success_msg "smbus2 Installation successful."
else
    log_failure_msg "smbus2 installation failed!"
    log_warning_msg "Please install it by manual: pip3 install smbus2"
fi

# TODO: Create daemon service or crontab by creating python scripts. 
# create bin folder and create python script to detect UPS's status.
log_action_msg "create $HOME/bin directory..."
/bin/mkdir -p $HOME/bin
export PATH=$PATH:$HOME/bin

# Create python script.
cat > $HOME/bin/upsPlus.py << EOF
#!/usr/bin/env python3

import os
import time
import smbus2
import logging
from ina219 import INA219,DeviceRangeError


# Define I2C bus
DEVICE_BUS = 1

# Define device i2c slave address.
DEVICE_ADDR = 0x17

# Set the threshold of UPS automatic power-off to prevent damage caused by battery over-discharge, unit: mV.
PROTECT_VOLT = 3700  

# Set the sample period, Unit: min default: 2 min.
SAMPLE_TIME = 2

# Instance INA219 and getting information from it.
ina_supply = INA219(0.00725, busnum=DEVICE_BUS, address=0x40)
ina_supply.configure()
supply_voltage = ina_supply.voltage()
supply_current = ina_supply.current()
supply_power = ina_supply.power()
print("-"*60)
print("------Current information of the detected Raspberry Pi------")
print("-"*60)
print("Raspberry Pi Supply Voltage: %.3f V" % supply_voltage)
print("Raspberry Pi Current Current Consumption: %.3f mA" % supply_current)
print("Raspberry Pi Current Power Consumption: %.3f mW" % supply_power)
print("-"*60)

# Batteries information
ina_batt = INA219(0.005, busnum=DEVICE_BUS, address=0x45)
ina_batt.configure()
batt_voltage = ina_batt.voltage()
batt_current = ina_batt.current()
batt_power = ina_batt.power()
print("-------------------Batteries information-------------------")
print("-"*60)
print("Voltage of Batteries: %.3f V" % batt_voltage)
try:
    if batt_current > 0:
        print("Battery Current (Charging) Rate: %.3f mA"% batt_current)
        print("Current Battery Power Supplement: %.3f mW"% batt_power)
    else:
        print("Battery Current (discharge) Rate: %.3f mA"% batt_current)
        print("Current Battery Power Consumption: %.3f mW"% batt_power)
        print("-"*60)
except DeviceRangeError:
     print("-"*60)
     print('Battery power is too high.')

# Raspberry Pi Communicates with MCU via i2c protocol.
bus = smbus2.SMBus(DEVICE_BUS)

aReceiveBuf = []
aReceiveBuf.append(0x00) 

# Read register and add the data to the list: aReceiveBuf
for i in range(1, 255):
    aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))

# Enable Back-to-AC fucntion.
# Enable: write 1 to register 0x19 == 25
# Disable: write 0 to register 0x19 == 25

bus.write_byte_data(DEVICE_ADDR, 25, 1)

# Reset Protect voltage
bus.write_byte_data(DEVICE_ADDR, 17, PROTECT_VOLT & 0xFF)
bus.write_byte_data(DEVICE_ADDR, 18, (PROTECT_VOLT >> 8)& 0xFF)
print("Successfully set the protection voltage to: %d mV" % PROTECT_VOLT)

if (aReceiveBuf[8] << 8 | aReceiveBuf[7]) > 4000:
    print('-'*60)
    print('Currently charging via Type C Port.')
elif (aReceiveBuf[10] << 8 | aReceiveBuf[9])> 4000:
    print('-'*60)
    print('Currently charging via Micro USB Port.')
else:
    print('-'*60)
    print('Currently not charging.')
# Consider shutting down to save data or send notifications
    if ((batt_voltage * 1000) < (PROTECT_VOLT + 200)):
        print('-'*60)
        print('The battery is going to dead! Ready to shut down!')
# It will cut off power when initialized shutdown sequence.
        bus.write_byte_data(DEVICE_ADDR, 24,240)
        os.system("sudo sync && sudo halt")
        while True:
            time.sleep(10)
EOF
log_action_msg "Create python3 script in location: $HOME/bin/upsPlus.py Successful"
# Upload the battery status to the data platform for subsequent technical support services 
# Create python file
cat > $HOME/bin/upsPlus_iot.py << EOF
#!/usr/bin/env python3

import time
import smbus2
import requests
from ina219 import INA219,DeviceRangeError
import random

DEVICE_BUS = 1
DEVICE_ADDR = 0x17
PROTECT_VOLT = 3700
SAMPLE_TIME = 2
FEED_URL = "https://api.52pi.com/feed"
time.sleep(random.randint(0, 59))

DATA = dict()

ina_supply = INA219(0.00725, busnum=DEVICE_BUS, address=0x40)
ina_supply.configure()
supply_voltage = ina_supply.voltage()
supply_current = ina_supply.current()
DATA['PiVccVolt'] = supply_voltage
DATA['PiIddAmps'] = supply_current

ina_batt = INA219(0.005, busnum=DEVICE_BUS, address=0x45)
ina_batt.configure()
batt_voltage = ina_batt.voltage()
batt_current = ina_batt.current()
DATA['BatVccVolt'] = batt_voltage
try:
    DATA['BatIddAmps'] = batt_current
except DeviceRangeError:
    DATA['BatIddAmps'] = 16000

bus = smbus2.SMBus(DEVICE_BUS)

aReceiveBuf = []
aReceiveBuf.append(0x00) # 占位符

for i in range(1,255):
    aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))

DATA['McuVccVolt'] = aReceiveBuf[2] << 8 | aReceiveBuf[1]
DATA['BatPinCVolt'] = aReceiveBuf[6] << 8 | aReceiveBuf[5]
DATA['ChargeTypeCVolt'] = aReceiveBuf[8] << 8 | aReceiveBuf[7]
DATA['ChargeMicroVolt'] = aReceiveBuf[10] << 8 | aReceiveBuf[9]

DATA['BatTemperature'] = aReceiveBuf[12] << 8 | aReceiveBuf[11]
DATA['BatFullVolt'] = aReceiveBuf[14] << 8 | aReceiveBuf[13]
DATA['BatEmptyVolt'] = aReceiveBuf[16] << 8 | aReceiveBuf[15]
DATA['BatProtectVolt'] = aReceiveBuf[18] << 8 | aReceiveBuf[17]
DATA['SampleTime'] = aReceiveBuf[22] << 8 | aReceiveBuf[21]
DATA['AutoPowerOn'] = aReceiveBuf[25]

DATA['OnlineTime'] = aReceiveBuf[31] << 24 | aReceiveBuf[30] << 16 | aReceiveBuf[29] << 8 | aReceiveBuf[28]
DATA['FullTime'] = aReceiveBuf[35] << 24 | aReceiveBuf[34] << 16 | aReceiveBuf[33] << 8 | aReceiveBuf[32]
DATA['OneshotTime'] = aReceiveBuf[39] << 24 | aReceiveBuf[38] << 16 | aReceiveBuf[37] << 8 | aReceiveBuf[36]
DATA['Version'] = aReceiveBuf[41] << 8 | aReceiveBuf[40]

DATA['UID0'] = "%08X" % (aReceiveBuf[243] << 24 | aReceiveBuf[242] << 16 | aReceiveBuf[241] << 8 | aReceiveBuf[240]) 
DATA['UID1'] = "%08X" % (aReceiveBuf[247] << 24 | aReceiveBuf[246] << 16 | aReceiveBuf[245] << 8 | aReceiveBuf[244]) 
DATA['UID2'] = "%08X" % (aReceiveBuf[251] << 24 | aReceiveBuf[250] << 16 | aReceiveBuf[249] << 8 | aReceiveBuf[248])

print(DATA)
r = requests.post(FEED_URL, data=DATA)
print(r.text)

EOF
log_success_msg "Create UPS Plus IoT customer service python script successful" 
# Add script to crontab 
log_action_msg "Add into general crontab list."

(crontab -l 2>/dev/null; echo "* * * * * /usr/bin/python3 $HOME/bin/upsPlus.py > /tmp/upsPlus.log") | crontab -
(crontab -l 2>/dev/null; echo "* * * * * /usr/bin/python3 $HOME/bin/upsPlus_iot.py > /tmp/upsPlus_iot.log") | crontab -
sudo systemctl restart cron

if [[ $? -eq 0 ]]; then
	log_action_msg "crontab has been created successful!"
else
	log_failure_msg "Create crontab failed!!"
	log_warning_msg "Please create crontab manually."
	log_action_msg "Usage: crontab -e"
fi 

# Testing and Greetings
if [[ -e $HOME/bin/upsPlus.py ]]; then 
    python3 $HOME/bin/upsPlus.py 
    if [[ $? -eq 0 ]]; then
       log_success_msg "UPS Plus Installation is Complete!"
       log_action_msg "-----------------More Information--------------------"
       log_action_msg "https://wiki.52pi.com/index.php/UPS_Plus_SKU:_EP-0136"
       log_action_msg "-----------------------------------------------------"
    else
       log_failure_msg "UPS Plus Installation is Incomplete!"
       log_action_msg "Please visit wiki for more information:"
       log_action_msg "-----------------------------------------------------"
       log_action_msg "https://wiki.52pi.com/index.php/UPS_Plus_SKU:_EP-0136"
       log_action_msg "-----------------------------------------------------"
    fi 
fi 
