import dataclasses

import wpiutil.wpistruct

class LedIO:

    @wpiutil.wpistruct.make_wpistruct(name="LedIOInputs")
    @dataclasses.dataclass
    class LedIOInputs:
        light1_r:float = 0
        light1_g:float = 0
        light1_b:float = 0

    def __init__(self):
        pass

    def updateInputs(self, inputs:LedIOInputs) -> None:
        pass

    def setColor(self, color_sqnc_name:str):
        '''
        changes current color to correspoding sequence of :param color_sqnc_name:
        '''
        pass

    def cycle_colors(self, iteration: int):
        '''
        runs through every one of the preset colors
        '''
        pass
    
    def rainbow(self, iteration: int):
        '''
        sets LEDs for moving rainbow pattern
        :param iteration: time value in a frag shader
        '''
        pass

    def refresh(self):
        '''
        put current set color onto actual LEDs

        should be called in periodic, not needed in independant functions
        '''
        pass
