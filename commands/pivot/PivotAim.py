### Imports
# Python Imports
import math

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems import Pivot
from util import *

# Intake Load Command
class PivotAim(Command):
    def __init__( self,
                  pivot:Pivot,
                  launchCalc:LaunchCalc
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.pivot = pivot
        self.launchCalc = launchCalc

        self.setName( "PivotAim" )
        self.addRequirements( pivot )

    def initialize(self) -> None: pass

    def execute(self) -> None:
        self.pivot.set( self.launchCalc.getLaunchAngle() )

    def end(self, interrupted:bool) -> None:
        pass

    def isFinished(self) -> bool:
        return self.pivot.atSetpoint()
    
    def runsWhenDisabled(self) -> bool: return False
