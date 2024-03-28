from commands2 import Command
from wpilib import RobotState

from subsystems import Led2

class LedDistraction(Command):
    def __init__(self, led:Led2):
        super().__init__()
        self.led = led
        self.setName( "Distraction" )
        self.addRequirements( led )

    def execute(self):
        self.led.runDistraction()
    
    def isFinished(self):
        return RobotState.isEStopped() or not RobotState.isTeleop()
