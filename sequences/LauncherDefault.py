import commands2

from commands import *
from subsystems import Launcher
from util import *

class LauncherDefault(commands2.SelectCommand):
    def __init__( self, 
                  launcher:Launcher, 
                  getDistance:typing.Callable[[],float] = lambda: 0.0, 
                  hasNote:typing.Callable[[],bool] = lambda: False,
                  isTargetAmp:typing.Callable[[],bool] = lambda: False,
                  useAutoStart:typing.Callable[[],bool] = lambda: True
                ):
        self.indexerHasNote = hasNote
        self.isTargetAmp = isTargetAmp
        self.useAutoStart = useAutoStart

        super().__init__(
            {
                "speaker": LauncherSpeaker( launcher, getDistance ),
                "amp": LauncherAmp( launcher ),
                "wait": commands2.cmd.none().withName("LauncherWait")
            },
            self.getState
        )

    def getState(self):
        if not self.indexerHasNote() or not self.useAutoStart():
            return "wait"
        elif self.isTargetAmp():
            return "amp"
        else:
            return "speaker"

    def initialize(self):
        super().initialize()
        self.setName( self._selectedCommand.getName() )
        