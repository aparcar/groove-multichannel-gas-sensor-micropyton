# Grove - Multichannel Gas Sensor via MicroPython

Quick (and incomplete) translation of Seeedstudios C library to MicroPython.

```Python
>>> from machine import I2C
>>> i2c = I2C(0, I2C.MASTER)
>>> from gas import Gas
>>>
>>> g = Gas(i2c)
>>> g.gas_dump()
49.79924 co
0.04426745 no2
8.446988 nh3
25441.62 c3h8
10013.97 c4h10
5070638.0 ch4
29.81235 h2
39.73325 c2h50h
```

[Official Wiki](http://wiki.seeedstudio.com/Grove-Multichannel_Gas_Sensor)
[Official C Library](https://github.com/Seeed-Studio/Mutichannel_Gas_Sensor)
