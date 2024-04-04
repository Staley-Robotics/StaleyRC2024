import typing

from commands2 import ConditionalCommand
import commands2.cmd

from commands import ClimberByStickMono
from subsystems import Climber

class ClimberDefault(ConditionalCommand):
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
        