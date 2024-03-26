from typing import overload

from wpilib import Color

class Led2IO:
    class Led2IOInputs:
        mode:bool = False

    def __init__(self): pass
    def updateInputs(self, inputs:Led2IOInputs): pass
    def run(self): pass
    def solid(self, color:Color): pass
    def strobe(self, color:list[Color], duration:float=0.0): pass
    def breathe(self, c1:Color, c2:Color, duration:float=0.0): pass
    def rainbow(self, cycleLength:float, duration:float=0.0): pass
    def wave(self, c1:Color, c2:Color, cycleLength:float, duration:float=0.0): pass
    def stripes(self, colors:list[Color], start:int=0, cycleLength:int=0, duration:float=0.0): pass
