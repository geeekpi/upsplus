#!/usr/bin/env python3

# '''Enable Auto-Shutdown Protection Function '''
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
PROTECT_VOLT = 3500

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

UID0 = "%08X" % (aReceiveBuf[243] << 24 | aReceiveBuf[242] << 16 | aReceiveBuf[241] << 8 | aReceiveBuf[240])
UID1 = "%08X" % (aReceiveBuf[247] << 24 | aReceiveBuf[246] << 16 | aReceiveBuf[245] << 8 | aReceiveBuf[244])
UID2 = "%08X" % (aReceiveBuf[251] << 24 | aReceiveBuf[250] << 16 | aReceiveBuf[249] << 8 | aReceiveBuf[248])
print('UID:' + UID0 + '/' + UID1 + '/' + UID2)

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
    if (str(batt_voltage)) == ("0.0"):
        print("Bad battery voltage value")
    if (str(batt_voltage)) != ("0.0"):
        if ((batt_voltage * 1000) < (PROTECT_VOLT + 200)):
            print('-'*60)
            print('The battery is going to dead! Ready to shut down!')
# It will cut off power when initialized shutdown sequence.
            bus.write_byte_data(DEVICE_ADDR, 24,240)
            os.system("sudo sync && sudo halt")
            while True:
                time.sleep(10)

