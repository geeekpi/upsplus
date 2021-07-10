#!/usr/bin/env python3

import os
import time
import json
import smbus2  # Required: smbus2 - pip3 install smbus2
import requests

# How to enter into OTA mode:
# Method 1) Setting register in terminal: i2cset -y 1 0x17 50 127 b
# Method 2) Remove all power connections and batteries, and then hold the power button, insert the batteries.

# Define device bus and address, and firmware url.
DEVICE_BUS = 1
DEVICE_ADDR = 0x18
UPDATE_URL = "https://api.52pi.com/update"

# instance of bus.
bus = smbus2.SMBus(DEVICE_BUS)
aReceiveBuf = []

for i in range(240, 252):
    aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))

UID0 = "%08X" % (aReceiveBuf[3] << 24 | aReceiveBuf[2] << 16 | aReceiveBuf[1] << 8 | aReceiveBuf[0])
UID1 = "%08X" % (aReceiveBuf[7] << 24 | aReceiveBuf[6] << 16 | aReceiveBuf[5] << 8 | aReceiveBuf[4])
UID2 = "%08X" % (aReceiveBuf[11] << 24 | aReceiveBuf[10] << 16 | aReceiveBuf[9] << 8 | aReceiveBuf[8])

r = requests.post(UPDATE_URL, data={"UID0": UID0, "UID1": UID1, "UID2": UID2})
# You can also specify your version, so you can rollback/forward to the specified version
# r = requests.post(UPDATE_URL, data={"UID0":UID0, "UID1":UID1, "UID2":UID2, "ver":7})
r = json.loads(r.text)
if r['code'] != 0:
    print('Can not get the firmware due to:' + r['reason'])
    exit(r['code'])
else:
    print('Pass the authentication, downloading the latest firmware...')
    req = requests.get(r['url'])
    if req.status_code == 404:
        print('version not found!')
        exit(-1)
    with open("/tmp/firmware.bin", "wb") as f:
        f.write(req.content)
    print("Download firmware successful.")

    print(
        "The firmware starts to be upgraded, please keep the power on, interruption in the middle will cause "
        "unrecoverable failure of the UPS!")
    with open("/tmp/firmware.bin", "rb") as f:
        while True:
            data = f.read(16)
            for i in range(len(list(data))):
                bus.write_byte_data(0x18, i + 1, data[i])
            bus.write_byte_data(0x18, 50, 250)
            time.sleep(0.1)
            print('.', end='', flush=True)

            if len(list(data)) == 0:
                bus.write_byte_data(0X18, 50, 0)
                print('.', flush=True)
                print('The firmware upgrade is complete, please disconnect all power/batteries and reinstall to use '
                      'the new firmware.')
                os.system("sudo halt")
                while True:
                    time.sleep(10)
