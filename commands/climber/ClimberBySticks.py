from commands2 import Command
from wpimath import applyDeadband

from subsystems import Climber
from util import *

# Intake Load Command
class ClimberBySticks(Command):
    def __init__( self,
                  climber:Climber,
                  leftStick:typing.Callable[[],float] = lambda: ( 0.0 ),
                  rightStick:typing.Callable[[],float] = lambda: ( 0.0 )
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.climber = climber
        self.leftStick = leftStick
        self.rightStick = rightStick
        self.position = 0.0

        self.setName( "ClimbBySticks" )
        self.addRequirements( climber )

    def initialize(self) -> None:
        pass

    def execute(self) -> None:
        lStick = applyDeadband( self.leftStick(), 0.05 )
        rStick = applyDeadband( self.rightStick(), 0.05 )
        self.climber.set( lStick, rStick )

    def end(self, interrupted:bool) -> None:
        self.climber.set( 0.0, 0.0 )

    def isFinished(self) -> bool:
        lStick = applyDeadband( self.leftStick(), 0.05 )
        rStick = applyDeadband( self.rightStick(), 0.05 )
        return lStick == 0.0 and rStick == 0.0
    
    def runsWhenDisabled(self) -> bool:
        return False
