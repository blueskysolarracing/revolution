from dataclasses import dataclass, field
from logging import getLogger
from typing import ClassVar
from time import sleep

from revolution.application import Application
from revolution.environment import Endpoint

import st7565  # type:ignore
import xglcd_font as font  # type:ignore

_logger = getLogger(__name__)


@dataclass
class Display(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.DISPLAY
    d1: st7565.Glcd = field(init=False)
    d2: st7565.Glcd = field(init=False)
    JetBrains13x20: font.XglcdFont = field(init=False)
    JetBrains13x21: font.XglcdFont = field(init=False)
    Font5x7: font.XglcdFont = field(init=False)
    Liberation_Sans20x28: font.XglcdFont = field(init=False)
    current_cruise: bool

    # display design based on google slides that you can find here
    # https://docs.google.com/presentation/d/1P_kAPFkVbpgUW_R5nXAC8cFNGyiidCfmwuXg6XJ8BWc/edit?usp=sharing

    # instantiate the two object for two display and run init for controller
    # also create Font object to later write with
    def __post_init__(self) -> None:
        self.d1 = st7565.Glcd()
        self.d2 = st7565.Glcd()
        self.d1.init()
        self.d2.init()
        # TODO generate new JetBrains13x21 font to have all characters
        self.JetBrains13x20 = font.XglcdFont("display_data/JetBrains_Mono13x20.c", 13, 20, 97)  # noqa: E501
        self.JetBrains13x21 = font.XglcdFont("display_data/JetBrains_Mono13x21_Symbol.c", 13, 21, 32)  # noqa: E501
        self.Liberation_Sans20x28 = font.XglcdFont("revolution/display_data/Liberation_Sans20x28_Numbers.c", 20, 28, 46)  # noqa: E501
        self.Font5x7 = font.XglcdFont("display_data/font5x7.c", 5, 7, 32)

    # draw blue sky logo, wait for a while, then draw the default screen
    def startup(self) -> None:
        self.d1.draw_symbol("logo", 0, 0)
        self.d2.draw_symbol("logo", 0, 0)
        self.d1.flip()
        self.d1.flip()
        sleep(3)
        self.draw(0, False)

    # draw display
    def draw(self, choice: int = 0, debug: bool = False) -> None:
        with self.environment.read() as data:
            if data.bms_fault:
                flag = 4
            elif data.ignition:
                flag = 3
            elif data.cruise != self.current_cruise:  # TODO how long to keep
                if data.cruise:
                    flag = 1
                else:
                    flag = 0
                self.current_cruise = data.cruise
            elif data.battery_low_volt:
                flag = 5
            else:
                flag = 0

        if debug:
            self.debug()
        else:
            self.drawD1()
            self.drawD2(choice, flag)

    # D1 only needs one cause it always show the same thing
    def drawD1(self) -> None:
        with self.environment.read() as data:
            solar = data.solar_power
            motor = data.motor_power
            battery = data.battery_power
            speed = data.speed_kph
            eco = data.eco_mode
            direction = data.direction
            headlight = data.headlight
            battery_warning = data.battery_warning
            hazard = data.hazard_lights_status
            indicatorR = data.right_indicator_light_status
            indicatorL = data.left_indicator_light_status

        # clear buffer
        self.d1.clear_back_buffer()

        # draw labels
        if solar >= 0:
            solarS = "Solar: +%4dW" % int(solar)
        else:
            solarS = "Solar: -%4dW" % abs(int(solar))
        if motor >= 0:
            motorS = "Motor: +%4dW" % int(motor)
        else:
            motorS = "Motor: -%4dW" % abs(int(motor))
        if battery >= 0:
            batteryS = "Batt:  +%4dW" % int(battery)
        else:
            batteryS = "Batt:  -%4dW" % abs(int(battery))

        self.d1.draw_string(solarS, self.Font5x7, x=0, y=5, spacing=1)
        self.d1.draw_string(motorS, self.Font5x7, x=0, y=15, spacing=1)
        self.d1.draw_string(batteryS, self.Font5x7, x=0, y=30, spacing=1)

        # draw leaf symbol
        if eco:
            self.d1.draw_symbol(symbol="leaf", x=10, y=52)
        # draw forward or backward indicator
        if direction:
            self.d1.draw_string("F", self.Font5x7, x=36, y=53, invert=True)
        else:
            self.d1.draw_string("R", self.Font5x7, x=36, y=53, invert=True)
        # draw headlight symbol
        if headlight:
            self.d1.draw_symbol(symbol="headlight", x=54, y=52)
        # draw battery warning
        if battery_warning:
            self.d1.draw_symbol(symbol="batt", x=84, y=0)
        # draw hazard
        if hazard:
            self.d1.draw_symbol(symbol="hazard", x=106, y=0)
        # draw direction indicator
        if indicatorR:
            self.d1.draw_string("->", self.Font5x7, x=116, y=50)
        if indicatorL:
            self.d1.draw_string("<-", self.Font5x7, x=80, y=50)

        # draw divider line
        self.d1.draw_line(x1=79, y1=0, x2=79, y2=63, color=1)

        # draw speed
        self.d1.draw_string("km/h", self.Font5x7, x=91, y=50)
        speedS = "%3d" % int(speed)
        if speed < 100:
            self.d1.draw_string(speedS[1:], self.Liberation_Sans20x28,
                                x=85, y=16, spacing=0)
        else:
            self.d1.draw_string(speedS, self.JetBrains13x21,
                                x=85, y=19, spacing=0)

        # write to display
        self.d1.flip()

    # D2 will choose what to draw depending on driver choices (choice)
    # or the fault screens (flag)
    def drawD2(self, choice: int, flag: int) -> None:
        self.d2.clear_back_buffer()
        if flag != 0:
            match flag:
                case 1:
                    self.cruiseActivate()
                case 2:
                    self.cruiseDeactivate()
                case 3:
                    self.ignitionOff()
                case 4:
                    self.bmsFault()
                case 5:
                    self.lowVolt()
                case _:
                    self.youFuckedUp()
        else:
            match choice:
                case 0:
                    self.default()
                case 1:
                    self.detailed()
                case 2:
                    self.status()
                case _:
                    self.youFuckedUp()
        self.d2.flip()

    # drawing funcions for D2
    def default(self) -> None:
        with self.environment.read() as data:
            motor_state = data.motor_state
            vfm = data.vfm
            battery = data.battery_soc

        # to make formating easier
        if battery > 99:
            battery = 99

        match motor_state:
            case 0:
                motor_stateS = "OFF"
            case 1:
                motor_stateS = "PEDAL"
            case 2:
                motor_stateS = "CRUISE"
            case 3:
                motor_stateS = "REGEN"
            case _:
                motor_stateS = "OFF"

        # draw motor state
        self.d2.draw_string(motor_stateS, self.JetBrains13x20,
                            x=49, y=25, spacing=0)
        # draw vfm
        self.d2.draw_string("VFM", self.JetBrains13x20, x=49, y=45, spacing=0)
        # draw colons with rectangle cause font doesnt include them
        self.d2.fill_rectangle(x1=90, y1=48, w=2, h=3, color=1)
        self.d2.fill_rectangle(x1=90, y1=54, w=2, h=3, color=1)
        self.d2.draw_string(("%d" % vfm), self.JetBrains13x21,
                            x=98, y=44, spacing=0)
        # draw battery state of charge
        self.d2.draw_string(("%2d" % int(battery)), self.Liberation_Sans20x28,
                            x=0, y=16, spacing=1)
        self.d2.draw_string("%", self.Font5x7, x=19, y=52)
        # draw divider line
        self.d2.draw_line(x1=44, y1=0, x2=44, y2=63, color=1)

    def lowVolt(self) -> None:
        with self.environment.read() as data:
            battery = data.battery_soc
            voltage = data.battery_low_volt

        # draw battery state of charge
        self.d2.draw_string(("%2d" % int(battery)), self.Liberation_Sans20x28,
                            x=0, y=16, spacing=1)
        self.d2.draw_string("%", self.Font5x7, x=19, y=52)
        # draw divider line
        self.d2.draw_line(x1=44, y1=0, x2=44, y2=63, color=1)
        # draw warning and voltage
        self.d2.draw_string("LOW SUPP", self.Font5x7, x=59, y=41)
        self.d2.draw_string("VOLTAGE", self.Font5x7, x=65, y=52)
        self.d2.draw_symbol("attention", x=44, y=5)
        self.d2.draw_string(("%2.1f" % voltage),
                            self.JetBrains13x21, x=75, y=9, spacing=0)
        self.d2.draw_string("V", self.JetBrains13x20, x=115, y=9, spacing=0)

    def detailed(self) -> None:
        with self.environment.read() as data:
            solar_power = int(data.solar_power)
            solar_voltage = abs(int(data.solar_voltage))
            solar_current = abs(int(data.solar_current))
            motor_power = int(data.motor_power)
            motor_voltage = abs(int(data.motor_voltage))
            motor_current = abs(int(data.motor_current))
            batt_power = int(data.battery_power)
            batt_voltage = abs(int(data.battery_voltage))
            batt_current = abs(int(data.battery_current))

        if solar_power >= 0:
            self.d2.draw_string("Solar:+%4dW(%3dV,%2dA)" %
                                (solar_power, solar_voltage, solar_current),
                                self.Font5x7, x=0, y=5)
        else:
            self.d2.draw_string("Solar:-%4dW(%3dV,%2dA)" %
                                (abs(solar_power), solar_voltage, solar_current),  # noqa: E501
                                self.Font5x7, x=0, y=5)
        if motor_power >= 0:
            self.d2.draw_string("Motor:+%4dW(%3dV,%2dA)" %
                                (motor_power, motor_voltage, motor_current),
                                self.Font5x7, x=0, y=28)
        else:
            self.d2.draw_string("Motor:-%4dW(%3dV,%2dA)" %
                                (abs(motor_power), motor_voltage, motor_current),  # noqa: E501
                                self.Font5x7, x=0, y=28)
        if batt_power >= 0:
            self.d2.draw_string("Batt: +%4dW(%3dV,%2dA)" %
                                (batt_power, batt_voltage, batt_current),
                                self.Font5x7, x=0, y=51)
        else:
            self.d2.draw_string("Batt: -%4dW(%3dV,%2dA)" %
                                (abs(batt_power), batt_voltage, batt_current),
                                self.Font5x7, x=0, y=51)

    def status(self) -> None:
        with self.environment.read() as data:
            lv_power = data.battery_low_volt_power
            lv_voltage = abs(data.battery_low_volt_voltage)
            lv_current = abs(data.battery_low_volt_current)
            temp = data.max_package_temp
            bb = data.bb_status
            mc = data.mc_status
            bms = data.bms_status
            ppt = data.ppt_status
            rad = data.rad_status

        if lv_power >= 0:
            self.d2.draw_string("LV: +%2.1fW(%2.1fV,%1.2fA)" %
                                (lv_power, lv_voltage, lv_current),
                                self.Font5x7, x=0, y=5, spacing=0)
        else:
            self.d2.draw_string("LV: -%2.1fW(%2.1fV,%1.2fA)" %
                                (lv_power, lv_voltage, lv_current),
                                self.Font5x7, x=0, y=5)

        self.d2.draw_string("Max pack temp: %3.1fC" % temp,
                            self.Font5x7, x=0, y=28)

        if bb:
            self.d2.draw_string("BB", self.Font5x7, x=8, y=51, invert=True)
        if mc:
            self.d2.draw_string("MC", self.Font5x7, x=28, y=51, invert=True)
        if bms:
            self.d2.draw_string("BMS", self.Font5x7, x=48, y=51, invert=True)
        if ppt:
            self.d2.draw_string("PPT", self.Font5x7, x=74, y=51, invert=True)
        if rad:
            self.d2.draw_string("RAD", self.Font5x7, x=100, y=51, invert=True)

    def cruiseActivate(self) -> None:
        self.d2.draw_string("CRUISE CONTROL", self.Font5x7, x=22, y=17)
        self.d2.draw_string("ACTIVATED", self.Font5x7, x=37, y=40, invert=True)  # noqa: E501

    def cruiseDeactivate(self) -> None:
        self.d2.draw_string("CRUISE CONTROL", self.Font5x7, x=22, y=17)
        self.d2.draw_string("DEACTIVATED", self.Font5x7, x=31, y=40, invert=True)  # noqa: E501

    def ignitionOff(self) -> None:
        with self.environment.read() as data:
            hv = int(data.battery_high_volt_voltage)
            lv_voltage = data.battery_low_volt_voltage
            lv_power = int(data.battery_low_volt_power)
            battery_soc = int(data.battery_soc)

        self.d2.draw_string("HV: %dV" % hv, self.Font5x7, x=0, y=5)
        self.d2.draw_string("LV: %2.1f (%dW)" % (lv_voltage, lv_power),
                            self.Font5x7, x=0, y=28)
        self.d2.draw_string("Battery: %d%%" % battery_soc,
                            self.Font5x7, x=0, y=51)
        self.d2.draw_string("SLEEPING", self.Font5x7, x=75, y=5)

    def bmsFault(self) -> None:
        with self.environment.read() as data:
            bms_fault_type = data.bms_fault_type
            fault_therm = data.fault_therm
            fault_cell = data.fault_cell

        # 0=OVERTEMP, 1=OVERVOLT, 2=UNDERVOLT, 3=OVERCUR
        match bms_fault_type:
            case 0:
                self.d2.draw_string("OVERTEMP (THERM %2d)" % fault_therm,
                                    self.Font5x7, x=22, y=51)
            case 1:
                self.d2.draw_string("OVERVOTE (CELL %2d)" % fault_cell,
                                    self.Font5x7, x=22, y=51)
            case 2:
                self.d2.draw_string("UNDERVOLT (CELL %2d)" % fault_cell,
                                    self.Font5x7, x=16, y=51)
            case 3:
                self.d2.draw_string("OVERCURRENT",
                                    self.Font5x7, x=4, y=51)
            case _:
                self.youFuckedUp()

        self.d2.draw_string("BMS FAULT DETECTED", self.Font5x7, x=10, y=5)
        self.d2.draw_string("CAR", self.Font5x7, x=43, y=28)
        self.d2.draw_string("OFF", self.Font5x7, x=67, y=28, invert=True)

    # debug by drawing pixel by pixel and then clearing once finish drawing
    # should draw from top left downwards column by column to bottom right
    def debug(self) -> None:
        self.d1.clear_back_buffer()
        self.d1.flip()
        self.d2.clear_back_buffer()
        self.d2.flip()
        for x in range(128):
            for y in range(64):
                self.d1.draw_point(x, y, 1)
                self.d2.draw_point(x, y, 1)
                self.d1.flip()
                self.d2.flip()
        self.d1.clear_back_buffer()
        self.d1.flip()
        self.d2.clear_back_buffer()
        self.d2.flip()

    def youFuckedUp(self) -> None:
        exit()  # TODO
