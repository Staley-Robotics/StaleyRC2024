### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems import Intake
from util import *

# Intake Load Command
class IntakeHandoff(Command):
    def __init__( self,
                  intake:Intake,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.intake = intake
        self.setName( "IntakeHandoff" )
        self.addRequirements( intake )

    def initialize(self) -> None:
        self.intake.setBrake(False)

    def execute(self) -> None:
        self.intake.set(Intake.IntakeSpeeds.Handoff)
    
    def end(self, interrupted:bool) -> None:
        self.intake.set(Intake.IntakeSpeeds.Stop)

    def isFinished(self) -> bool:
        return False
        return not self.intake.hasNote()
    
    def runsWhenDisabled(self) -> bool: return False