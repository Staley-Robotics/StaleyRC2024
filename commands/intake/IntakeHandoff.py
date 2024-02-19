### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems.Intake import Intake
from util import *

# Intake Load Command
class IntakeHandoff(Command):
    def __init__( self,
                  intake:Intake,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.intake = intake
        self.intake.setBrake(False)

        self.setName( "IntakeHandoff" )
        self.addRequirements( intake )

    def initialize(self) -> None:
        pass

    def execute(self) -> None:
        self.intake.set(Intake.IntakeSpeeds.Handoff)
    
    def end(self) -> None:
        self.intake.set(Intake.IntakeSpeeds.Stop)

    def isFinished(self) -> bool: 
        return not self.intake.hasNote()
    
    def runsWhenDisabled(self) -> bool: return False
