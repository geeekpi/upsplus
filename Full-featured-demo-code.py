#!/usr/bin/env python3

# Description：
'''This is the demo code for all the functions of UPS Plus.
Advanced users can select the functions they need through the function options provided in the code below to customize and develop them to meet their needs.
'''

import time
import smbus2
import logging
from ina219 import INA219,DeviceRangeError

DEVICE_BUS = 1
DEVICE_ADDR = 0x17
PROTECT_VOLT = 3700
SAMPLE_TIME = 2

ina_supply = INA219(0.00725, busnum=DEVICE_BUS, address=0x40)
ina_supply.configure()
supply_voltage = ina_supply.voltage()
supply_current = ina_supply.current()
supply_power = ina_supply.power()
print("Raspberry Pi power supply voltage: %.3f V" % supply_voltage)
print("Current current consumption of Raspberry Pi: %.3f mA" % supply_current)
print("Current power consumption of Raspberry Pi: %.3f mW" % supply_power)


ina_batt = INA219(0.005, busnum=DEVICE_BUS, address=0x45)
ina_batt.configure()
batt_voltage = ina_batt.voltage()
batt_current = ina_batt.current()
batt_power = ina_batt.power()
print("Batteries Voltage: %.3f V" % batt_voltage)
try:
    if batt_current > 0:
        print("Battery current (charging), rate: %.3f mA" % batt_current)
        print("Current battery power supplement: %.3f mW" % batt_power)
    else:
        print("Battery current (discharge), rate: %.3f mA" % batt_current)
        print("Current battery power consumption: %.3f mW" % batt_power)
except DeviceRangeError:
    print('Battery power is too high.')

bus = smbus2.SMBus(DEVICE_BUS)

aReceiveBuf = []
aReceiveBuf.append(0x00)   # Placeholder

for i in range(1,255):
    aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))

print("Current processor voltage: %d mV"% (aReceiveBuf[2] << 8 | aReceiveBuf[1]))
print("Current Raspberry Pi report voltage: %d mV"% (aReceiveBuf[4] << 8 | aReceiveBuf[3]))
print("Current battery port report voltage: %d mV"% (aReceiveBuf[6] << 8 | aReceiveBuf[5])) # This value is inaccurate during charging
print("Current charging interface report voltage (Type C): %d mV"% (aReceiveBuf[8] << 8 | aReceiveBuf[7]))
print("Current charging interface report voltage (Micro USB): %d mV"% (aReceiveBuf[10] << 8 | aReceiveBuf[9]))

if (aReceiveBuf[8] << 8 | aReceiveBuf[7]) > 4000:
    print('Currently charging through Type C.')
elif (aReceiveBuf[10] << 8 | aReceiveBuf[9]) > 4000:
    print('Currently charging via Micro USB.')
else:
    print('Currently not charging.')   # Consider shutting down to save data or send notifications 

print("Current battery temperature (estimated): %d degC"% (aReceiveBuf[12] << 8 | aReceiveBuf[11])) # Learned from the battery internal resistance change, the longer the use, the more stable the data.
print("Full battery voltage: %d mV"% (aReceiveBuf[14] << 8 | aReceiveBuf[13]))
print("Battery empty voltage: %d mV"% (aReceiveBuf[16] << 8 | aReceiveBuf[15]))
print("Battery protection voltage: %d mV"% (aReceiveBuf[18] << 8 | aReceiveBuf[17]))
print("Battery remaining capacity: %d %%"% (aReceiveBuf[20] << 8 | aReceiveBuf[19]))  # At least one complete charge and discharge cycle is passed before this value is meaningful.
print("Sampling period: %d Min"% (aReceiveBuf[22] << 8 | aReceiveBuf[21]))
if aReceiveBuf[23] == 1:
    print("Current power state: normal")
else:
    print("Current power status: off")

if aReceiveBuf[24] == 0:
    print('No shutdown countdown!')
else:
    print("Shutdown countdown: %d sec"% (aReceiveBuf[24]))

if aReceiveBuf[25] == 1:
    print("Automatically turn on when there is external power supply!")
else:
    print("Does not automatically turn on when there is an external power supply!")
if aReceiveBuf[26] == 0:
    print('No restart countdown!')
else:
    print("Restart countdown: %d sec"% (aReceiveBuf[26]))

print("Accumulated running time: %d sec"% (aReceiveBuf[31] << 24 | aReceiveBuf[30] << 16 | aReceiveBuf[29] << 8 | aReceiveBuf[28]))
print("Accumulated charged time: %d sec"% (aReceiveBuf[35] << 24 | aReceiveBuf[34] << 16 | aReceiveBuf[33] << 8 | aReceiveBuf[32]))
print("This running time: %d sec"% (aReceiveBuf[39] << 24 | aReceiveBuf[38] << 16 | aReceiveBuf[37] << 8 | aReceiveBuf[36]))
print("Version number: %d "% (aReceiveBuf[41] << 8 | aReceiveBuf[40]))

#The following code demonstrates resetting the protection voltage
# bus.write_byte_data(DEVICE_ADDR, 17,PROTECT_VOLT & 0xFF)
# bus.write_byte_data(DEVICE_ADDR, 18,(PROTECT_VOLT >> 8)& 0xFF)
# print("Successfully set the protection voltage as: %d mV"% PROTECT_VOLT)

#The following code demonstrates resetting the sampling period
# bus.write_byte_data(DEVICE_ADDR, 21,SAMPLE_TIME & 0xFF)
# bus.write_byte_data(DEVICE_ADDR, 22,(SAMPLE_TIME >> 8)& 0xFF)
# print("Successfully set the sampling period as: %d Min"% SAMPLE_TIME)

# Set to shut down after 240 seconds (can be reset repeatedly)
# bus.write_byte_data(DEVICE_ADDR, 24,240)
bus.write_byte_data(DEVICE_ADDR, 24,240)

# Cancel automatic shutdown
# bus.write_byte_data(DEVICE_ADDR, 24,0)

# Automatically turn on when there is an external power supply (If the automatic shutdown is set, when there is an external power supply, it will shut down and restart the board.)
# 1) If you want to completely shut down, please don't turn on the automatic startup when there is an external power supply.
# 2) If you want to shut down the UPS yourself because of low battery power, you can shut down the UPS first, and then automatically recover when the external power supply comes.
# 3) If you simply want to force restart the power, please use another method.
# 4) Set to 0 to cancel automatic startup.
# 5) If this automatic startup is not set, and the battery is exhausted and shut down, the system will resume work when the power is restored as much as possible, but it is not necessarily when the external power supply is plugged in.
# bus.write_byte_data(DEVICE_ADDR, 25,1)
bus.write_byte_data(DEVICE_ADDR, 25,1)

# Force restart (simulate power plug, write the corresponding number of seconds, shut down 5 seconds before the end of the countdown, and then turn on at 0 seconds.)
# bus.write_byte_data(DEVICE_ADDR, 26,30)
bus.write_byte_data(DEVICE_ADDR, 26, 10)

# Restore factory settings (clear memory, clear learning parameters, can not clear the cumulative running time, used for after-sales purposes.)
# bus.write_byte_data(DEVICE_ADDR, 27,1)

# Enter the OTA state (the user demo program should not have this thing, after setting, unplug the external power supply, unplug the battery, reinstall the battery, install the external power supply (optional), you can enter the OTA mode and upgrade the firmware.)
# bus.write_byte_data(DEVICE_ADDR, 50,127)

# Serial Number 
UID0 = "%08X" % (aReceiveBuf[243] << 24 | aReceiveBuf[242] << 16 | aReceiveBuf[241] << 8 | aReceiveBuf[240])
UID1 = "%08X" % (aReceiveBuf[247] << 24 | aReceiveBuf[246] << 16 | aReceiveBuf[245] << 8 | aReceiveBuf[244]) 
UID2 = "%08X" % (aReceiveBuf[251] << 24 | aReceiveBuf[250] << 16 | aReceiveBuf[249] << 8 | aReceiveBuf[248])
print("Serial Number is:" + UID0 + "-" + UID1 + "-" + UID2 )
