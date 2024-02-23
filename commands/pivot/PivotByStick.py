### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

from wpimath import applyDeadband

# Our Imports
from subsystems import Pivot
from util import *

# Intake Load Command
class PivotByStick(Command):
    def __init__( self,
                  pivot:Pivot,
                  stick:typing.Callable = lambda: ( 0.0 ),
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.pivot = pivot
        self.stick = stick
        self.position = 0.0

        self.setName( "PivotByStick" )
        self.addRequirements( pivot )

    def initialize(self) -> None: pass

    def execute(self) -> None:
        # Describes the normalization function to distribute stick positions evenly across pivot rotations
        self.position = (applyDeadband(self.stick(), 0.04) - Pivot.PivotPositions.Downward.get())/(Pivot.PivotPositions.Upward.get() - Pivot.PivotPositions.Downward.get())
        
        self.pivot.set(self.position)

    def end(self, interrupted:bool) -> None:
        pass # May be set to zero in future, but for now: assuming hold position

    def isFinished(self) -> bool:
        return False
        return self.pivot.atSetpoint()
    
    def runsWhenDisabled(self) -> bool: return False
