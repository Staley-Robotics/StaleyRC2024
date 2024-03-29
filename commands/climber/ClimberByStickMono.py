from commands2 import Command

from subsystems import Climber
from commands.climber.ClimberBySticks import ClimberBySticks
from util import *

# Intake Load Command
class ClimberByStickMono(ClimberBySticks):
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