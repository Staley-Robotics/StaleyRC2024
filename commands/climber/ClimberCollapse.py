### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems import Climber
from util import *

# Intake Load Command
class ClimberCollapse(Command):
    def __init__( self,
                  climber:Climber,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.climber = climber
        self.setName( "ClimberCollapse" )
        self.addRequirements( climber )

    def initialize(self) -> None:
        self.climber.setBrake(True)

    def execute(self) -> None:
        self.climber.set(Climber.ClimberPositions.Bottom.get(), Climber.ClimberPositions.Bottom.get())
    
    def end(self, interrupted:bool) -> None:
        self.climber.stop()

    def isFinished(self) -> bool:
        return False
        return self.climber.atSetpoint()
    
    def runsWhenDisabled(self) -> bool: return False