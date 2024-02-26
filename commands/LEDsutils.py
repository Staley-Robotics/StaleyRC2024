from typing import Callable, Optional
import commands2
from wpiutil import SendableBuilder

from subsystems import LEDs

class cycleColors(commands2.Command):
    """
    Cycles through the colors in the color sequence chart provided by Austin
    """

    def __init__(self, LED = LEDs):
        super().__init__()
        self.m_led = LED
        self.time_pressed = 0 #by units of 1/50th a second
        self.setName( "cycleColors" )
        self.addRequirements( LED )
    
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
    """
    Cycles through the colors in the color sequence chart provided by Austin... but fast
    """
    def __init__(self, LED = LEDs):
        super().__init__()
        self.m_led = LED
        self.time_pressed = 0 #by units of 1/50th a second
        self.setName( "DiStrAcTiON" )
        self.addRequirements( LED )
    
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
    """
    Sets the current color sequence to the default color (either red or blue depending on alliance)
    """
    def __init__(self, LED = LEDs):
        super().__init__()
        self.m_led = LED
        self.time_pressed = 0 #by units of 1/50th a second
        self.setName( "defaultColor" )
        self.addRequirements( LED )
    
    def initialize(self):
        self.m_led.defaultColor()
        self.time_pressed = 0
        print("defaultColor/initialize/Complete")


    def execute(self):
        pass
        # self.m_led.defaultColor()
        # if self.time_pressed % 7 == 0 and self.time_pressed >= 20:
        #     self.m_led.defaultColor()
        # print("defaultColor/execute/happened")

    def isFinished(self) -> bool: return False

    def runsWhenDisabled(self) -> bool: return True


class rainbow(commands2.Command):
    """
    Cycles through each pixel and sets them to a different color in the rainbow
    """
    def __init__(self, LED = LEDs):
        super().__init__()
        self.m_led = LED
        # self.time_pressed = 0 #by units of 1/50th a second
        self.setName( "rainbow" )
        self.addRequirements( LED )
    
    def initialize(self):
        self.m_led.rainbow()
        # self.time_pressed = 0
        print("rainbow/initialize/Complete")


    def execute(self):
        self.m_led.rainbow()
        # if self.time_pressed % 10 == 0 and self.time_pressed >= 1000:
        #     self.m_led.rainbow()
        # the above commented code is not needed (it kinda broke the LEDs)
        print("rainbow/execute/happened")

    def isFinished(self) -> bool: return False

    def runsWhenDisabled(self) -> bool: return True

class rainbowReset(commands2.Command):
    """
    Resets the rainbow color sequence

    Only necessary if the rainbow breaks
    """
    def __init__(self, LED = LEDs):
        super().__init__()
        self.m_led = LED
        # self.time_pressed = 0 #by units of 1/50th a second
        self.setName( "rainbowReset" )
        self.addRequirements( LED )
    
    def initialize(self):
        self.m_led.rainbowReset()
        # self.time_pressed = 0
        print("rainbowReset/initialize/Complete")


    def execute(self):
        pass
        # self.m_led.rainbowReset()
        # # if self.time_pressed % 10 == 0 and self.time_pressed >= 1000:
        # #     self.m_led.rainbow()
        # # the above commented code is not needed (it kinda broke the LEDs)
        # print("rainbowReset/execute/happened")

    def isFinished(self) -> bool: return False

    def runsWhenDisabled(self) -> bool: return True


class addColor(commands2.Command):
    """
    Adds a color to an empty rainbow color sequence. (MUST BE EMPTY TO WORK PROPERLY)

    r -> red value in RGB
    g -> green value in RGB
    b -> blue value in RGB
    """
    def __init__(self, LED = LEDs, r = int, g = int, b = int):
        super().__init__()
        self.m_led = LED
        self.r = r #red value
        self.g = g #green value
        self.b = b #blue value
        # self.time_pressed = 0 #by units of 1/50th a second
        self.setName( "addColor" )
        self.addRequirements( LED )
    
    def initialize(self):
        self.m_led.addColor(r=self.r, b=self.b, g=self.g)
        # self.time_pressed = 0
        print("addColor/initialize/Complete")


    def execute(self):
        pass
        # self.m_led.addColor()
        # # if self.time_pressed % 10 == 0 and self.time_pressed >= 1000:
        # #     self.m_led.addColor()
        # # the above commented code is not needed (it kinda broke the LEDs)
        # print("addColor/execute/happened")

    def isFinished(self) -> bool: return False

    def runsWhenDisabled(self) -> bool: return True