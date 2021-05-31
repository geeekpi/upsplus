 # Firmware Version History & Update Schedule

------
Current firmware version:V7

| Version | Date |
| :--------:   | :-----:  |
| V3 | - |
| V7 | 2021-05-13 |
| V8 | 2021-05-31 |

Version V3:

 - This is the earliest firmware available to the public.

Version V7:

 - Fix the issue of not able to perform shutdown operation when there is an external power supply.
 - [ Full Voltage and Empty Voltage ] Can be edited manually [#16][1]

Version V8:

 - Fix the problem that the power button cannot be turned off when [Back-To-AC Auto Power up] is set.
 - Fix an intermittent freeze during 400kHz I2C access.

Known issues being resolved:

- [ ] Firmware runs sometimes freeze and time is no longer accumulated.
 


  [1]: https://github.com/geeekpi/upsplus/issues/16 "Issue #16"
