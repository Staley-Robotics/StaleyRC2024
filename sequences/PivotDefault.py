import commands2

from commands import *
from subsystems import Pivot
from util import *

class PivotDefault(commands2.ConditionalCommand):
    def __init__(self, pivot:Pivot, getAngle:typing.Callable[[],float], hasNote:typing.Callable[[],bool] = lambda:False):
        super().__init__(
            #PivotSpeaker(pivot),
            PivotAim(pivot, getAngle),
            PivotHandoff(pivot),
            hasNote
        )

    def initialize(self):
        super().initialize()
        self.setName( self.selectedCommand.getName() )
        