### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems.Pivot import Pivot
from util import *

# Intake Load Command
class PivotByStick(Command):
    def __init__( self,
                  pivot:Pivot,
                  stick:float = lambda: ( 0.0 ),
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
        self.position = (self.stick - self.pivot.PivotPositions.Downward)\
                        /\
                        (self.pivot.PivotPositions.Upward - self.pivot.PivotPositions.Downward)
        
        self.pivot.set(self.position)

    def end(self, interrupted:bool) -> None:
        pass # May be set to zero in future, but for now: assuming hold position

    def isFinished(self) -> bool:
        return self.pivot.atSetpoint()
    
    def runsWhenDisabled(self) -> bool: return False
