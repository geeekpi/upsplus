# ''' Update the status of batteries to IoT platform '''
import time
import smbus2
import requests
from ina219 import INA219,DeviceRangeError
import random

DEVICE_BUS = 1
DEVICE_ADDR = 0x17
PROTECT_VOLT = 3700
SAMPLE_TIME = 2
FEED_URL = "https://api.thekoziolfoundation.com/feed"
time.sleep(random.randint(0, 59))

DATA = dict()

ina = INA219(0.00725,address=0x40)
ina.configure()
DATA['PiVccVolt'] = ina.voltage()
DATA['PiIddAmps'] = ina.current()

ina = INA219(0.005,address=0x45)
ina.configure()
DATA['BatVccVolt'] = ina.voltage()
try:
    DATA['BatIddAmps'] = ina.current()
except DeviceRangeError:
    DATA['BatIddAmps'] = 16000

bus = smbus2.SMBus(DEVICE_BUS)

aReceiveBuf = []
aReceiveBuf.append(0x00)  

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
DATA['AutoPowerOn'] = aReceiveBuf[24]

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
