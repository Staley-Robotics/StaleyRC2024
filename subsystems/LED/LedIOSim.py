from wpilib import *
import wpimath.units

from util import *
from subsystems import LedIO 

#NOTE: this is just LedIOActual renamed atm

class LedIOSim(LedIO):
    
    def __init__(self, PWMPort:int):
        # Tunables

        ## init LED
        self.m_led = wpilib.AddressableLED(PWMPort)

        # Some other init stufs
        self.m_led.setSyncTime(wpimath.units.microseconds(10))

        self.m_ledLength = 22 # Num of LEDs on strip

        # Reuse buffer -- wdym?
        # Length is expensive to set, so only set it once, then just update data
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

        #currently uses color updated spicifically from commands, maybe shift to modes to call funcs for blinky or cycling colors
        #better explained: change fromthe various methods, to just defining multiple funcs as frag shaders and swapping between them
        self.currentColor = self.color_sqncs['default']

        self.m_led.setData(self.currentColor)
        self.m_led.start()


    def updateInputs(self, inputs:LedIO.LedIOInputs):
        inputs.current_color = self.currentColor

    def setColor(self, color_sqnc_name:str):
        '''
        changes current color
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