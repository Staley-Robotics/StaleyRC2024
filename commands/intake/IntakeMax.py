### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems import Intake
from util import *

# Intake Load Command
class IntakeMax(Command):
    def __init__( self,
                  intake:Intake,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.intake = intake

        self.setName( "IntakeMax" )
        self.addRequirements( intake )

    def initialize(self) -> None:
        self.intake.setBrake(True)

    def execute(self) -> None:
        self.intake.set(Intake.IntakeSpeeds.Max.get())
    
    def end(self, interrupted:bool) -> None:
        self.intake.set(Intake.IntakeSpeeds.Stop.get())

    def isFinished(self) -> bool: 
        return False
    
    def runsWhenDisabled(self) -> bool: return False