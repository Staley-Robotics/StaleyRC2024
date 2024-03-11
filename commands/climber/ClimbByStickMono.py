from commands2 import Command

from subsystems import Climber
from util import *

# Intake Load Command
class ClimbByStickMono(Command):
    def __init__( self,
                  climber:Climber,
                  stick:typing.Callable = lambda: ( 0.0 ),
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.climber = climber
        self.stick = stick
        self.position = 0.0

        self.setName( "ClimbByStickMono" )
        self.addRequirements( climber )

    def initialize(self) -> None:
        pass

    def execute(self) -> None:
        self.climber.moveLeftClimber(self.stick())
        self.climber.moveRightClimber(self.stick())

    def end(self, interrupted:bool) -> None:
        pass

    def isFinished(self) -> bool:
        return False
    
    def runsWhenDisabled(self) -> bool:
        return False
