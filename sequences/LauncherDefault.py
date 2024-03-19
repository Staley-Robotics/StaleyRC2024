import commands2

from commands import *
from subsystems import Launcher
from util import *

class LauncherDefault(commands2.ConditionalCommand):
    def __init__(self, launcher:Launcher, startCondition:typing.Callable[[],bool] = lambda:False):
        super().__init__(
            LauncherSpeaker( launcher ),
            commands2.cmd.none().withName("LauncherWait"),
            startCondition
        )

    def initialize(self):
        super().initialize()
        self.setName( self.selectedCommand.getName() )
        