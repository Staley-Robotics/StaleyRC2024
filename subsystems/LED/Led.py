"""
Taken from Andy in github
"""

import wpilib
import wpimath.units

from commands2 import Subsystem

from subsystems import LedIO

from util import *

class LED(Subsystem):
    class LEDColors:
        defaultColor = (255, 0, 0)
    
    def __init__(self, led:LedIO) -> None:
        self.led = led
        self.ledInputs = led.LedIOInputs
        self.ledLogger = NetworkTableInstance.getDefault().getStructTopic( "/LED", LedIO.LedIOInputs ).publish()

        self.offline = NTTunableBoolean( "/DisableSubsystem/LED", False, persistent=True )

    def periodic(self) -> None:
        #logging
        self.led.updateInputs(self.ledInputs)
        self.ledLogger.set(self.ledInputs)

        # Run Subsystem
        if  wpilib.RobotBase.isDisabled() or self.offline.get():
            #logic copied from launcher -- doesn't actually disable?
            self.defaultColor()

        self.led.refresh()
    
    ## START shell funcs for LedIOActual methods
    
    def setColor(self, color_sqnc_name:str):
        """
        changes current color to correspoding sequence of :param color_sqnc_name:
        """
        self.led.setColor(color_sqnc_name)
    
    def cycle_colors(self, iteration: int):
        '''
        runs through every one of the preset colors
        '''
        self.led.cycle_colors(iteration)
    
    def rainbow(self, iteration: int):
        '''
        sets LEDs for moving rainbow pattern
        :param iteration: time value in a frag shader
        '''
        self.led.rainbow(iteration)
    
    ## END shell funcs for LedIOActual Methods