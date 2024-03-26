from commands2 import Command
from wpilib import RobotState

from subsystems import Led2

class LedButton(Command):
    def __init__(self, led:Led2):
        super().__init__()
        self.led = led
        self.setName( "LedButton" )
        self.addRequirements( led )

    def initialize(self):
        if RobotState.isDisabled():
            self.setName( "Celebration" )
        elif RobotState.isTeleop():
            self.setName( "Distraction" )

    def execute(self):
        if RobotState.isDisabled():
            self.led.runStaleyCelebration()
        elif RobotState.isTeleop():
            self.led.runDistraction()
    
    def isFinished(self):
        return not RobotState.isDisabled() and not RobotState.isTeleop()

    def runsWhenDisabled(self):
        return True
