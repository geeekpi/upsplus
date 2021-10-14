 # Firmware Version History & Update Schedule

------
Current firmware version:V7

| Version | Date |
| :--------:   | :-----:  |
| V3 | - |
| V7 | 2021-05-13 |
| V8 | 2021-05-31 |
| V9 | 2021-07-21 |
| V10 | 2021-19-02 |

Version V3:

 - This is the earliest firmware available to the public.

Version V7:

 - Fix the issue of not able to perform shutdown operation when there is an external power supply.
 - [ Full Voltage and Empty Voltage ] Can be edited manually [#16][1]

Version V8:

 - Fix the problem that the power button cannot be turned off when [Back-To-AC Auto Power up] is set.
 - Fix an intermittent freeze during 400kHz I2C access.

Version V9:

 - The UPS (hardware version PCB01c) no longer uses NCE20P70G/NCE20P85G as a power supply switch because the supplier has been out of stock for a long time and there is no direct replacement, so it is replaced by other similar devices.
 - [Bug fix] Due to compiler optimization, some execution logic may be skipped in some cases, which does not affect the basic I2C operation, but some readings may be incorrect.
 - [Bug fix] The manual voltage can not be set, please note that the manual setting threshold voltage only affects the charging logic, and does not change the parameters of the battery itself.

Version V10:

 - After 30 days of continuous and multi-faceted testing, the V10 firmware fixes a random freeze issue, mainly as a result of possible interruptions in I2C accesses causing I2C lock-ups, a known issue with ST's ST controllers, using the FAE recommended method to fix.


  [1]: https://github.com/geeekpi/upsplus/issues/16 "Issue #16"
