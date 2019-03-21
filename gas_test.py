from machine import I2C

i2c = I2C(0, I2C.MASTER)
from gas import Gas

g = Gas(i2c)
g.gas_dump()
