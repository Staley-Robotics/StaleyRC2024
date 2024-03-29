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
                  getPose:typing.Callable[[],Pose2d],
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.pivot = pivot
        self.getPose = getPose

        self.aimAdjust = NTTunableFloat( "/Config/PivotPositions/AutoAimAdjust", 0.0, persistent=True )
        self.calcAim = NTTunableFloat( "/Logging/PivotCalc", 0.0 )
        
        self.setName( "PivotAim" )
        self.addRequirements( pivot )

    def initialize(self) -> None: pass

    def execute(self) -> None:
        pose = self.getPose()
        target = CrescendoUtil.getSpeakerTarget()
        height = CrescendoUtil.getSpeakerHeight()
        pivotHeight = CrescendoUtil.getRobotPivotHeight()

        distance = pose.translation().distance( target )
        posRad = math.atan( (height-pivotHeight) / distance )
        pos = math.degrees( posRad )
        pos += self.aimAdjust.get()
        self.calcAim.set( pos )
        self.pivot.set(pos) # Assumed that the calculation for pivot @ distance from target is done elsewhere

    def end(self, interrupted:bool) -> None:
        self.calcAim.set( 0.0 )
        pass # May be set to zero in future, but for now: assuming hold position

    def isFinished(self) -> bool:
        return self.pivot.atSetpoint()
    
    def runsWhenDisabled(self) -> bool: return False
