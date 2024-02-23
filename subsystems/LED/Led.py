"""
Taken from Andy in github
"""

import wpilib
import wpimath.units

from commands import Subsystem

from util import *

class LEDs(Subsystem):
    def __init__(self, port=0) -> None:
        super().__init__()

        # PWM port 9
        # Must be a PWM header, not MXP or DIO
        self.m_led = wpilib.AddressableLED(port)

        # Some other init stufs
        self.m_led.setSyncTime(wpimath.units.microseconds(10))

        # Num of LEDs on strip
        self.m_ledLength = 22

        # Reuse buffer
        # Length is expensive to set, so only set it once, then just update data
        self.m_led.setLength(self.m_ledLength)

        self.m_ledData = [wpilib.AddressableLED.LEDData(255, 0, 0) for i in range(self.m_ledLength)]

        # ----------INITIALIZING COLOR SEQUENCES----------
        # Default color sequence (autonomous is this but flashing)
        self.default_color = []
        for i in range(self.m_ledDefaultLength.get()):
            self.default_color.append( wpilib.AddressableLED.LEDData(0, 200, 200)) #alliance color (red: 255, 0, 0 OR blue: 0, 0, 255)

        # Color sequence if robot has note
        self.hasNoteColor = []
        for i in range(self.m_ledDefaultLength.get()):
            self.hasNoteColor.append( wpilib.AddressableLED.LEDData(250, 127, 0)) #orange

        # Color sequence if robot has note and has a 75-89% chance of shooting to the right spot
        self.hasNote7589Color = []
        for i in range(self.m_ledDefaultLength.get()):
            self.hasNote7589Color.append( wpilib.AddressableLED.LEDData(255, 255, 0)) #yellow

        # Color sequence if robot has note and has a 90-100% chance of shooting to the right spot
        self.hasNote90100Color = []
        for i in range(self.m_ledDefaultLength.get()):
            self.hasNote90100Color.append( wpilib.AddressableLED.LEDData(0, 255, 0)) #green

        # Color sequence for designate amp (idk why the name is like this)
        self.designateAmpColor = []
        for i in range(self.m_ledDefaultLength.get()):
            self.designateAmpColor.append( wpilib.AddressableLED.LEDData(255, 0, 255)) #purple

        # Endgame color sequence
        self.endgameColor = []
        for i in range(self.m_ledDefaultLength.get()):
            self.endgameColor.append( wpilib.AddressableLED.LEDData(255, 255, 255)) #white
        
        self.currentColor = self.default_color

        # Set the data
        self.m_led.setData(self.currentColor)
        self.m_led.start()

    def cycleColors(self):
        """
        Sets the entire LED strip to one color.

        Cycles throught the possible color combinations
        """
        if self.currentColor == self.default_color: #if default, set to hasNote
            self.currentColor = self.hasNoteColor

        elif self.currentColor == self.hasNoteColor: #if hasNot, set to hasNote7589
            self.currentColor = self.hasNote7589Color

        elif self.currentColor == self.hasNote7589Color: #if hasNote7589, set to hasNote90100
            self.currentColor = self.hasNote90100Color

        elif self.currentColor == self.hasNote90100Color: #if hasNote90100, set to designateAmp
            self.currentColor = self.designateAmpColor

        elif self.currentColor == self.designateAmpColor: #if disignateAmp, set to endgame
            self.currentColor = self.endgameColor
        
        elif self.currentColor == self.endgameColor: #if endgame, set to default
            self.currentColor = self.default_color

        # match self.currentColor:
        #     case self.default_color:
        #         self.currentColor = self.hasNoteColor

        self.update()

    def DiStrAcTiON(self):
        """
        Sets the entire LED strip to one color.

        Cycles throught the possible color combinations
        """
        if self.currentColor == self.default_color: #if default, set to hasNote
            self.currentColor = self.hasNoteColor

        elif self.currentColor == self.hasNoteColor: #if hasNot, set to hasNote7589
            self.currentColor = self.hasNote7589Color

        elif self.currentColor == self.hasNote7589Color: #if hasNote7589, set to hasNote90100
            self.currentColor = self.hasNote90100Color

        elif self.currentColor == self.hasNote90100Color: #if hasNote90100, set to designateAmp
            self.currentColor = self.designateAmpColor

        elif self.currentColor == self.designateAmpColor: #if disignateAmp, set to endgame
            self.currentColor = self.endgameColor
        
        elif self.currentColor == self.endgameColor: #if endgame, set to default
            self.currentColor = self.default_color  


        self.update()
            
    def defaultColor(self):
        """
        Sets the color of the LEDS to the default color. (either blue or red depending on what alliance we are on)
        """
        self.currentColor = self.default_color
        self.update()

    def update(self):
        self.m_led.setData(self.currentColor)