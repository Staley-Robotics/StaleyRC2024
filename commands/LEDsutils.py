from typing import Callable, Optional
import commands2
from commands2.subsystem import Subsystem
from wpiutil import SendableBuilder

from subsystems import LEDs

class cycleColors(commands2.Command):
    def __init__(self, LED = LEDs):
        super().__init__()
        self.m_led = LED
        self.time_pressed = 0 #by units of 1/50th a second
    
    def initialize(self):
        self.m_led.cycleColors()
        self.time_pressed = 0
        print("cycleColors/initialize/Complete")


    def execute(self): pass
    #     self.m_led.cycleColors()
    #     if self.time_pressed % 7 == 0 and self.time_pressed >= 100:
    #         self.m_led.cycleColors()
    #     print("cycleColors/execute/happened")
    #     print(self.time_pressed)

    def isFinished(self) -> bool: return False

    def runsWhenDisabled(self) -> bool: return True

class DiStrAcTiON(commands2.Command):
    def __init__(self, LED = LEDs):
        super().__init__()
        self.m_led = LED
        self.time_pressed = 0 #by units of 1/50th a second
    
    def initialize(self):
        self.m_led.DiStrAcTiON()
        self.time_pressed = 0
        print("DiStrAcTiON/initialize/Complete")


    def execute(self):
        self.m_led.DiStrAcTiON()
        if self.time_pressed % 7 == 0 and self.time_pressed >= 20:
            self.m_led.DiStrAcTiON()
        print("cycleColors/execute/happened")
        print(self.time_pressed)

    def isFinished(self) -> bool: return False

    def runsWhenDisabled(self) -> bool: return True



class defaultColor(commands2.Command):
    def __init__(self, LED = LEDs):
        super().__init__()
        self.m_led = LED
        self.time_pressed = 0 #by units of 1/50th a second
    
    def initialize(self):
        self.m_led.defaultColor()
        self.time_pressed = 0
        print("defaultColor/initialize/Complete")


    def execute(self):
        self.m_led.defaultColor()
        if self.time_pressed % 7 == 0 and self.time_pressed >= 20:
            self.m_led.defaultColor()
        print("defaultColor/execute/happened")

    def isFinished(self) -> bool: return False

    def runsWhenDisabled(self) -> bool: return True