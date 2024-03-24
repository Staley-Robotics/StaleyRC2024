import commands2

from commands import *
from subsystems import Launcher
from util import *

class LauncherDefault(commands2.ConditionalCommand):
    def __init__( self, 
                  launcher:Launcher, 
                  getDistance:typing.Callable[[],float] = lambda: 0.0, 
                  hasNote:typing.Callable[[],bool] = lambda: False
                ):
        super().__init__(
            LauncherSpeaker( launcher, getDistance ),
            commands2.cmd.none().withName("LauncherWait"),
            hasNote()
        )

    def initialize(self):
        super().initialize()
        self.setName( self.selectedCommand.getName() )
        