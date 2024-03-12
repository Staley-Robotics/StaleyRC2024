from commands2 import Command

from subsystems import Climber
from util import *

# Intake Load Command
class ClimbBySticks(Command):
    def __init__( self,
                  climber:Climber,
                  leftStick:typing.Callable[[],None] = lambda: ( 0.0 ),
                  rightStick:typing.Callable[[],None] = lambda: ( 0.0 )
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
        self.climber.move(self.leftStick(), self.rightStick())

    def end(self, interrupted:bool) -> None:
        pass

    def isFinished(self) -> bool:
        return False
    
    def runsWhenDisabled(self) -> bool:
        return False
