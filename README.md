# upsplus
## UPS Plus is a new generation of UPS power management module.
It is an `improved` version of the original UPS prototype.
* It has been fixed the bug that UPS could not charge and automatically power off during work time. 
* It can not only perform good battery power management, but also provide stable voltage output and RTC functions. 
* At the same time,it support for FCP, AFC, SFCP fast charge protocol, support BC1.2 charging protocol, support battery terminal current/voltage monitoring and support two-way monitoring of charge and discharge.
* It can provide programmable PVD function. 
- Power Voltage Detector (PVD) can be used to detect if batteries voltage is below or above configured voltage. 
- Once this function has been enabled, it will monitoring your batteries voltage, and you can control whether or not shut down Raspberry Pi via simple bash script or python script. 
- This function will protect your batteries from damage caused by excessive discharge. 
* It can provide Adjustable data sampling Rate.
- This function allows you to adjust the data sampling rate so that you can get more detailed battery information and also it will consume some power.
- The data sampling information can communicate with the upper computer device through the I2C protocol. 
* UPS Plus supports the OTA firmware upgrade function. 
- Once there is a new firmware update, it is very convenient for you to upgrade firmware for UPS Plus. The firmware upgrade can be completed only by connecting to the Internet,and execute a python script. 
* Support battery temperature monitoring and power-down memory function.
* UPS Plus can be set to automatically start the Raspberry Pi after the external power comes on. 
- The programmable shutdown and forced restart function will provide you with a remote power-off restart management method. 
- That means you don’t need to go Unplug the power cable or press the power button to cut off the power again. 
- You can set the program to disconnect the power supply after a few seconds after the Raspberry Pi is shut down properly.
- And you can also reconnect the power supply after a forced power failure to achieve a remote power-off and restart operation. 
- Once it was setting up, you don't need to press power button to boot up your device which is very suitable for smart home application scenarios.
## How to use
* Download Repository and execute:
```bash
cd ~
curl -Lso- https://git.io/JLygb
```
When encountering low battery, it will automatically shut down and turn off the UPS and it will restart when AC power comes.
## How to upgrade firmware of UPS.
* Upgrade firmware will be via `OTA` style, `OTA` means `over the air`, it allows you `update` or `upgrade` firmware via internet.
- 1. Make sure Raspberry Pi can access internet.
- 2. Download Repository from `GitHub`.
```bash
cd ~
git clone https://github.com/geeekpi/upsplus.git
cd upsplus/
python3 OTA_firmware_upgrade.py
```
When `upgrade` process is finished, it will `shutdown` your Raspberry Pi automatically, and you `need` to disconnect the charger and remove all batteries from UPS and then insert the batteries again, then press the power button to turn on the UPS.
*** NOTE: Do not assemble UPS with Raspberry Pi with Batteries in it *** 

## Battery List.
* A list of Batteries used by UPSPlus users community.

| Brand | Model | Volt | mAmp | SAMPLE_TIME | Testing | Time |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| DoublePow | ICR18650 | 3.7 | 2600 | 3 | X | 

Don't forget replace PROTECT_VOLT variable value, from Battery Volt value. Example: Battery 3.6V = 3600

## FAQ 
* Q: Why does the battery light go off sometime and lights up in a while?
- A: This is because the power chip performs battery re-sampling, and the purpose is that the data of inferior batteries is inaccurate during the sampling process.

* Q: Why is the power cut off every once in a while?
- A: Please check the battery charging current, the data discharge direction or the charging direction. If the load is too large, the charging may not be enough, which will cause this problem.
* Q: What kind of wall charger should I use?
- A: If the load is normal, it is recommended to use an ordinary 5V@2A charging head. If you need to carry a slightly higher load, it is recommended to use a fast charging source. We support FCP, AFC, SFCP protocols Fast charging source.
* Q: Can I directly input 9V and 12V to the USB port?
- A: No, if you must do this, you must remove the DP, DM and other related detection pins, and ensure that the power supply is stable.
* Q: I heard howling, why is this?
- A: Because of the no-load protection mechanism, the howling will disappear after the load is installed.
