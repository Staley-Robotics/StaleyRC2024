from commands2 import Command

from subsystems import Climber
from commands.climber.ClimbBySticks import ClimbBySticks
from util import *

# Intake Load Command
class ClimbByStickMono(ClimbBySticks):
    def __init__( self,
                  climber:Climber,
                  stick:typing.Callable[[],float] = lambda: ( 0.0 ),
                ):
        # CommandBase Initiation Configurations
        super().__init__(
            climber,
            stick,
            stick
        )
        self.setName( "ClimbByStickMono" )