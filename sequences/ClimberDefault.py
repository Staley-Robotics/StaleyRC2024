import commands2

from commands import *
from subsystems import Climber
from util import *

class ClimberDefault(commands2.ConditionalCommand):
    def __init__(self, climber:Climber, axis:typing.Callable[[],float], useAxis:typing.Callable[[],bool]):
        super().__init__(
            #PivotSpeaker(pivot),
            ClimberByStickMono(climber, axis),
            commands2.cmd.none().withName("ClimberWait"),
            useAxis
        )

    def initialize(self):
        super().initialize()
        self.setName( self.selectedCommand.getName() )
        