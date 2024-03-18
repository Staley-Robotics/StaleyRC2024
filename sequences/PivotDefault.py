import commands2

from commands import *
from subsystems import Pivot
from util import *

class PivotDefault(commands2.ConditionalCommand):
    def __init__(self, pivot:Pivot, getPose:typing.Callable[[],Pose2d], hasNote:typing.Callable[[],bool] = lambda:False):
        super().__init__(
            #PivotSpeaker(pivot),
            PivotAim(pivot, getPose),
            PivotHandoff(pivot),
            hasNote
        )

    def initialize(self):
        super().initialize()
        self.setName( self.selectedCommand.getName() )
        