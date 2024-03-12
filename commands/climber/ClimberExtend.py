### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems import Climber
from util import *

# Intake Load Command
class ClimberExtend(Command):
    def __init__( self,
                  climber:Climber,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.climber = climber
        self.setName( "ClimberExtend" )
        self.addRequirements( climber )

    def initialize(self) -> None:
        self.climber.setBrake(True)

    def execute(self) -> None:
        self.climber.set(Climber.ClimberPositions.Top.get())
    
    def end(self, interrupted:bool) -> None:
        self.climber.stop()

    def isFinished(self) -> bool:
        return not self.climber.atSetpoint()
    
    def runsWhenDisabled(self) -> bool: return False