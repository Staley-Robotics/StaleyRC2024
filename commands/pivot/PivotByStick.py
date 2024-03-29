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
        # NTTunables
        self.deadband = NTTunableFloat( "/Config/Driver2/Deadband", 0.04, persistent=True )
        self.changeRate = NTTunableFloat( "/Config/Driver2/ChangeRate", 1.0, persistent=True )
        self.position = NTTunableFloat( "/Config/Driver2/PivotLastPos", 0.0, persistent=True )

        # CommandBase Initiation Configurations
        super().__init__()
        self.pivot = pivot
        self.stick = stick

        self.setName( "PivotByStick" )
        self.addRequirements( pivot )

    def initialize(self) -> None: pass

    def execute(self) -> None:
        # Describes the normalization function to distribute stick positions evenly across pivot rotations
        moveBy = applyDeadband(self.stick(), self.deadband.get())
        moveBy *= self.changeRate.get()
        self.position.set( min( max( self.position.get() + moveBy, Pivot.PivotPositions.Downward.get() ), Pivot.PivotPositions.Upward.get() ) )
        self.pivot.set(self.position.get())

    def end(self, interrupted:bool) -> None:
        pass # May be set to zero in future, but for now: assuming hold position

    def isFinished(self) -> bool:
        return self.pivot.atSetpoint()
    
    def runsWhenDisabled(self) -> bool: return False
