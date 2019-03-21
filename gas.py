from math import pow
from time import sleep


class Gas:
    DEFAULT_I2C_ADDR = 0x04

    ADDR_IS_SET = 0  # if this is the first time to run, if 1126, set
    ADDR_FACTORY_ADC_NH3 = 2
    ADDR_FACTORY_ADC_CO = 4
    ADDR_FACTORY_ADC_NO2 = 6

    ADDR_USER_ADC_HN3 = 8
    ADDR_USER_ADC_CO = 10
    ADDR_USER_ADC_NO2 = 12
    ADDR_IF_CALI = 14  # IF USER HAD CALI

    ADDR_I2C_ADDRESS = 20

    CH_VALUE_NH3 = 1
    CH_VALUE_CO = 2
    CH_VALUE_NO2 = 3

    CMD_ADC_RES0 = 1  # NH3
    CMD_ADC_RES1 = 2  # CO
    CMD_ADC_RES2 = 3  # NO2
    CMD_ADC_RESALL = 4  # ALL CHANNEL
    CMD_CHANGE_I2C = 5  # CHANGE I2C
    CMD_READ_EEPROM = 6  # READ EEPROM VALUE, RETURN UNSIGNED INT
    CMD_SET_R0_ADC = 7  # SET R0 ADC VALUE
    CMD_GET_R0_ADC = 8  # GET R0 ADC VALUE
    CMD_GET_R0_ADC_FACTORY = 9  # GET FACTORY R0 ADC VALUE
    CMD_CONTROL_LED = 10
    CMD_CONTROL_PWR = 11

    CO = 0
    NO2 = 1
    NH3 = 2
    C3H8 = 3
    C4H10 = 4
    CH4 = 5
    H2 = 6
    C2H5OH = 7

    adcValueR0_NH3_Buf = 0
    adcValueR0_C0_Buf = 0
    adcValueR0_NO2_Buf = 0

    def __init__(self, i2c, addr=DEFAULT_I2C_ADDR):
        self.i2c = i2c
        self.addr = addr
        self.version = self.get_version()

    def cmd(self, cmd, nbytes=2):
        self.i2c.writeto(self.addr, bytes(cmd))
        dta = 0
        raw = self.i2c.readfrom(self.addr, nbytes)
        for byte in raw:
            dta = dta * 256 + int(byte)

        if cmd == self.CH_VALUE_NH3:
            if dta > 0:
                self.adcValueR0_NH3_Buf = dta
            else:
                dta = self.adcValueR0_NH3_Buf
        elif cmd == self.CH_VALUE_CO:
            if dta > 0:
                self.adcValueR0_CO_Buf = dta
            else:
                dta = self.adcValueR0_CO_Buf
        elif cmd == self.CH_VALUE_NO2:
            if dta > 0:
                self.adcValueR0_NO2_Buf = dta
            else:
                dta = self.adcValueR0_NO2_Buf

        return dta

    def get_version(self):
        if self.cmd([self.CMD_READ_EEPROM, self.ADDR_IS_SET]) == 1126:
            print("version = 2")
            return 2
        else:
            print("version = 1")
            print("version currently not supported")
            from sys import exit

            exit(1)

    def change_addr(self, new_addr):
        self.cmd([35, new_addr])
        self.addr = new_addr

    def power_on(self):
        self.cmd([self.CMD_CONTROL_PWR, 1])

    def power_off(self):
        self.cmd([self.CMD_CONTROL_PWR, 0])

    def led_on(self):
        self.cmd([self.CMD_CONTROL_LED, 1])

    def led_off(self):
        self.cmd([self.CMD_CONTROL_LED, 0])

    def calc_gas(self, gas):
        self.led_on()

        A0_0 = self.cmd([6, self.ADDR_USER_ADC_HN3])
        A0_1 = self.cmd([6, self.ADDR_USER_ADC_CO])
        A0_2 = self.cmd([6, self.ADDR_USER_ADC_NO2])

        An_0 = self.cmd([self.CH_VALUE_NH3])
        An_1 = self.cmd([self.CH_VALUE_CO])
        An_2 = self.cmd([self.CH_VALUE_NO2])

        ratio0 = An_0 / A0_0 * (1023.0 - A0_0) / (1023.0 - An_0)
        ratio1 = An_1 / A0_1 * (1023.0 - A0_1) / (1023.0 - An_1)
        ratio2 = An_2 / A0_2 * (1023.0 - A0_2) / (1023.0 - An_2)

        c = 0.0

        if gas == self.CO:
            c = pow(ratio1, -1.179) * 4.385

        elif gas == self.NO2:
            c = pow(ratio2, 1.007) / 6.855
        elif gas == self.NH3:
            c = pow(ratio0, -1.67) / 1.47
        elif gas == self.C3H8:
            c = pow(ratio0, -2.518) * 570.164
        elif gas == self.C4H10:
            c = pow(ratio0, -2.138) * 398.107
        elif gas == self.CH4:
            c = pow(ratio1, -4.363) * 630.957
        elif gas == self.H2:
            c = pow(ratio1, -1.8) * 0.73
        elif gas == self.C2H5OH:
            c = pow(ratio1, -1.552) * 1.622

        if self.version == 2:
            self.led_off()

        return c or -3

    def display_eeprom(self):
        print("ADDR_IS_SET = ", self.cmd(self.CMD_READ_EEPROM, self.ADDR_IS_SET))
        print(
            "ADDR_FACTORY_ADC_NH3 = ",
            self.cmd(self.CMD_READ_EEPROM, self.ADDR_FACTORY_ADC_NH3),
        )
        print(
            "ADDR_FACTORY_ADC_CO = ",
            self.cmd(self.CMD_READ_EEPROM, self.ADDR_FACTORY_ADC_CO),
        )
        print(
            "ADDR_FACTORY_ADC_NO2 = ",
            self.cmd(self.CMD_READ_EEPROM, self.ADDR_FACTORY_ADC_NO2),
        )
        print(
            "ADDR_USER_ADC_HN3 = ",
            self.cmd(self.CMD_READ_EEPROM, self.ADDR_USER_ADC_HN3),
        )
        print(
            "ADDR_USER_ADC_CO = ", self.cmd(self.CMD_READ_EEPROM, self.ADDR_USER_ADC_CO)
        )
        print(
            "ADDR_USER_ADC_NO2 = ",
            self.cmd(self.CMD_READ_EEPROM, self.ADDR_USER_ADC_NO2),
        )
        print(
            "ADDR_I2C_ADDRESS = ", self.cmd(self.CMD_READ_EEPROM, self.ADDR_I2C_ADDRESS)
        )

    def do_calibrate(self):
        i = 0
        a0 = 0
        a1 = 0
        a2 = 0

        while True:
            a0 = self.cmd(self.CH_VALUE_NH3)
            a1 = self.cmd(self.CH_VALUE_CO)
            a2 = self.cmd(self.CH_VALUE_NO2)

            print("{}\t{}\t{}".format(a0, a1, a2))
            self.led_on()

            cnt = 0
            for i in range(20):
                if (a0 - self.cmd(self.CH_VALUE_NH3)) > 2 or (
                    self.cmd(self.CH_VALUE_NH3) - a0
                ) > 2:
                    cnt += 1
                if (a1 - self.cmd(self.CH_VALUE_CO)) > 2 or (
                    self.cmd(self.CH_VALUE_CO) - a1
                ) > 2:
                    cnt += 1
                if (a2 - self.cmd(self.CH_VALUE_NO2)) > 2 or (
                    self.cmd(self.CH_VALUE_NO2) - a2
                ) > 2:
                    cnt += 1

                if cnt > 5:
                    break

                sleep(1000)

            self.led_off()
            if cnt <= 5:
                break
            delay(200)

        print("write user adc value: ")
        print("{}\t{}\t{}".format(a0, a1, a2))

        tmp = []

        tmp[0] = 7

        tmp[1] = a0 >> 8
        tmp[2] = a0 & 0xFF

        tmp[3] = a1 >> 8
        tmp[4] = a1 & 0xFF

        tmp[5] = a2 >> 8
        tmp[6] = a2 & 0xFF

        self.cmd(self.addr, tmp, 7)

    def gas_dump(self):
        print(self.calc_gas(self.CO), "co")
        print(self.calc_gas(self.NO2), "no2")
        print(self.calc_gas(self.NH3), "nh3")
        print(self.calc_gas(self.C3H8), "c3h8")
        print(self.calc_gas(self.C4H10), "c4h10")
        print(self.calc_gas(self.CH4), "ch4")
        print(self.calc_gas(self.H2), "h2")
        print(self.calc_gas(self.C2H5OH), "c2h50h")
