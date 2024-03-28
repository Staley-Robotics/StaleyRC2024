from commands2 import Command
from wpilib import RobotState

from subsystems import Led2

class LedCelebration(Command):
    def __init__(self, led:Led2):
        super().__init__()
        self.led = led
        self.setName( "Celebration" )
        self.addRequirements( led )

    def execute(self):
        self.led.runStaleyCelebration()
    
    def isFinished(self):
        return RobotState.isEStopped() or not RobotState.isDisabled() 

    def runsWhenDisabled(self):
        return True
