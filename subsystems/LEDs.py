"""
Description: LEDs Container Class (Testing)
Version: 1
Date: 2024
"""

# FRC Imports
import wpilib
import wpimath.units
import commands2.button
import commands2

# Self made classes
from util import *
import math

class LEDs(commands2.Subsystem):
    def __init__(self, port=0) -> None:
        super().__init__()

        # PWM port 9
        # Must be a PWM header, not MXP or DIO
        self.m_led = wpilib.AddressableLED(port)

        # Some other init stufs
        self.m_led.setSyncTime(wpimath.units.microseconds(280))

        # NTTunables (made these tunables because fun)
        self.m_ledDefaultLength = NTTunableInt("LEDs/DefaultLength", 22, None, False)
        self.m_rainbowFirstPixelHue = NTTunableInt("LEDs/rainbowFirstPixelHue", 0, None, True)
        self.colorindexCUSWHYNOT = NTTunableInt("LEDs/colorindexCUSWHYNOT", 0, None, False)

        # Reuse buffer
        # Default to a length of 60, start empty output
        # Length is expensive to set, so only set it once, then just update data
        self.m_led.setLength(self.m_ledDefaultLength.get())    #So apparently self.m_ledDefaultLength.get() wasn't returning 22 or smthn idk
        self.m_ledData = []
        for i in range(self.m_ledDefaultLength.get()):
            self.m_ledData.append( wpilib.AddressableLED.LEDData(255, 0, 0) )


        # ----------INITIALIZE CUSTOM COLOR SEQUENCE----------
        self.rainbowColor = []
        for i in range(self.m_ledDefaultLength.get()):
            self.rainbowColor.append( wpilib.AddressableLED.LEDData() ) #blank LEDs


        # ----------INITIALIZE GAME COLOR SEQUENCES----------
        # Default color sequence (autonomous is this but flashing)
        self.default_color = []
        for i in range(self.m_ledDefaultLength.get()):
            self.default_color.append( wpilib.AddressableLED.LEDData(255, 0, 0)) #alliance color (red: 255, 0, 0 OR blue: 0, 0, 255)

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

        self.yellowPurple = []
        for i in range(self.m_ledDefaultLength.get()//2): #first half of the strip
            self.yellowPurple.append( wpilib.AddressableLED.LEDData(255, 255, 0)) #yellow
        for i in range(self.m_ledDefaultLength.get()//2): #second half of the strip
            self.yellowPurple.append( wpilib.AddressableLED.LEDData(255, 0, 255)) #purple

        self.default_color = self.yellowPurple
        
        self.currentColor = self.default_color

        # Set the data
        self.m_led.setData(self.currentColor)
        self.m_led.start()


    # ------------------COLOR CHANGING FUNCTIONS------------------
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


        self.update()

    def DiStrAcTiON(self):
        """
        Sets the entire LED strip to multiple different colors

        Cycles throught the possible color combinations

        Is a DiStRactIoN
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

        else: #else, set to default
            self.currentColor = self.default_color


        self.update()
            
    def defaultColor(self):
        """
        Sets the color of the LEDs to the default color. (either blue or red depending on what alliance we are on)
        """
        self.currentColor = self.default_color
        self.update()

    def rainbow(self):
        """
        Makes the LEDs go RAinBoW
        """

        self.currentColor = self.rainbowColor

        # For every pixel
        for i, value in enumerate(self.currentColor):
            # Calculate the hue - hue is easier for rainbows because the color
            # shape is a circle so only one value needs to precess
            hue = int((self.m_rainbowFirstPixelHue.get() + ((i+1) * 180 / len(self.currentColor))) % 180)
            
            # Set the value
            value.setHSV(hue, 255, 128)
            print(hue)

        # Increase by to make the rainbow "move"
        self.m_rainbowFirstPixelHue.set((self.m_rainbowFirstPixelHue.get() + 3)%180)
        # Check bounds

        # self.currentColor = self.rainbowColor

        self.update()

    def rainbowReset(self):
        """
        resets the rainbow color sequence

        use if the rainbow starts breaking (mainly for sim)
        """
        self.colorindexCUSWHYNOT.set(0)

        for i in range(self.m_ledDefaultLength.get()):
            self.rainbowColor[i] = ( wpilib.AddressableLED.LEDData() ) #blank LEDs

        self.update()

    def addColor(self, r, g, b):
        self.currentColor[self.colorindexCUSWHYNOT.get()] = wpilib.AddressableLED.LEDData(r, g, b)
        
        if self.colorindexCUSWHYNOT.get() == 21: #regulate this index so that no out_of_list_range errors occur
            self.colorindexCUSWHYNOT.set(0)
        else:
            self.colorindexCUSWHYNOT.set(self.colorindexCUSWHYNOT.get() + 1)

        self.update()


    # -----UPDATE FUNCTION----- (to be changed to periodic)
    def update(self):
        self.m_led.setData(self.currentColor)
       



    # New stuff (name for this section TBD)
    def periodic(self):
        self.update()

    def funcTBD(self):
        pass