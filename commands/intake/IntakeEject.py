### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command
from wpilib import Timer

# Our Imports
from subsystems.Intake import Intake
from util import *

# Intake Load Command
class IntakeEject(Command):
    def __init__( self,
                  intake:Intake,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.timer = Timer()
        self.intake = intake
        
        self.setName( "IntakeEject" )
        self.addRequirements( intake )

    def initialize(self) -> None:
        self.timer.reset()
        self.timer.start()
        self.intake.setBrake(False)

    def execute(self) -> None:
        self.intake.set(Intake.IntakeSpeeds.Eject)

    def end(self, interrupted:bool) -> None:
        self.timer.stop()
        self.intake.set(Intake.IntakeSpeeds.Stop)

    def isFinished(self) -> bool:
        return self.timer.hasElapsed(2.0)
    
    def runsWhenDisabled(self) -> bool: return False
