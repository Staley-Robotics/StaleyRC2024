from wpilib import *
import wpimath.units

from util import *
from subsystems import LedIO 

class LedIOActual(LedIO):
    
    def __init__(self, PWMPort:int):
        # Tunables

        ## init LED
        self.m_led = wpilib.AddressableLED(PWMPort)
        self.m_ledLength = 22 # Num of LEDs on strip
        self.m_led.setLength(self.m_ledLength)

        self.m_ledData = [wpilib.AddressableLED.LEDData(255, 0, 0) for i in range(self.m_ledLength)]

        # init color sequences
        self.color_sqncs = {
            'default': [wpilib.AddressableLED.LEDData(0, 200, 200) for i in range(self.m_ledLength)], #alliance - red or blue
            'has note': [wpilib.AddressableLED.LEDData(255, 127, 0) for i in range(self.m_ledLength)],
            '75-89 chance': [wpilib.AddressableLED.LEDData(255, 255, 0) for i in range(self.m_ledLength)],
            '90-100 chance': [wpilib.AddressableLED.LEDData(0, 255, 0) for i in range(self.m_ledLength)],
            'designate amp': [wpilib.AddressableLED.LEDData(255, 0, 255) for i in range(self.m_ledLength)],
            'endgame': [wpilib.AddressableLED.LEDData(255, 255, 255) for i in range(self.m_ledLength)],
        }

        self.m_led.setData(self.currentColor)
        self.m_led.start()


    def updateInputs(self, inputs:LedIO.LedIOInputs):
        #logs the active color on the first pixel of the led for testing purposes
        inputs.light1_r = self.currentColor[0].r
        inputs.light1_g = self.currentColor[0].g
        inputs.light1_b = self.currentColor[0].b

    def setColor(self, color_sqnc_name:str):
        '''
        changes current color to :param color_sqnc_name: from color_sqncs dict
        '''
        self.currentColor = self.color_sqncs[color_sqnc_name]

    def cycle_colors(self, iteration: int):
        '''
        runs through every one of the preset colors
        '''
        self.currentColor = self.color_sqncs[list(self.color_sqncs.keys())[iteration]]
    
    def rainbow(self, iteration: int):
        '''
        sets LEDs for moving rainbow pattern
        :param iteration: time value in a frag shader
        '''
        for i, data in enumerate(self.currentColor):
            data.setHSV((i + iteration)%180, 255, 255)

    def refresh(self):
        '''
        put current set color onto actual LEDs

        should be called in periodic, not needed in independant functions
        '''
        self.m_led.setData(self.currentColor)