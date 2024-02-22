### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems import Intake
from util import *

# Intake Load Command
class IntakeLoad(Command):
    def __init__( self,
                  intake:Intake,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.intake = intake

        self.setName( "IntakeLoad" )
        self.addRequirements( intake )

    def initialize(self) -> None:
        self.intake.setBrake(True)

    def execute(self) -> None:
        self.intake.set(Intake.IntakeSpeeds.Load.get())
    
    def end(self, interrupted:bool) -> None:
        self.intake.set(Intake.IntakeSpeeds.Stop.get())

    def isFinished(self) -> bool: 
        return self.intake.hasNote()
    
    def runsWhenDisabled(self) -> bool: return False