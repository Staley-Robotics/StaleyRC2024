import commands2

from subsystems import LED

class runLedRainbow(commands2.Command):
    def __init__(self, led: LED):
        self.led = led
        self.iteration = 0
    
    def initialize(self):
        self.iteration = 0
    
    def execute(self):
        self.led.rainbow(self.iteration)
        self.iteration = (self.iteration+1)
    
    def end(self, interrupted: bool):
        self.led.setColor('default')
    
    def isFinished(self) -> bool:
        return False