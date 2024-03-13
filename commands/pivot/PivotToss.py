### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems import Pivot
from util import *

# Intake Load Command
class PivotToss(Command):
    def __init__( self,
                  pivot:Pivot,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.pivot = pivot

        self.setName( "PivotToss" )
        self.addRequirements( pivot )

    def initialize(self) -> None: pass

    def execute(self) -> None:
        self.pivot.set(Pivot.PivotPositions.Toss.get())

    def end(self, interrupted:bool) -> None:
        pass # May be set to zero in future, but for now: assuming hold position

    def isFinished(self) -> bool:
        return self.pivot.atSetpoint()
    
    def runsWhenDisabled(self) -> bool: return False
