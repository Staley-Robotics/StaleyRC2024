import typing

from commands2 import SelectCommand
import commands2.cmd

from commands import LauncherSpeaker, LauncherAmp, LauncherToss
from subsystems import Launcher

class LauncherDefault(SelectCommand):
    def __init__( self, 
                  launcher:Launcher, 
                  getDistance:typing.Callable[[],float] = lambda: 0.0, 
                  isIndexerReady:typing.Callable[[],bool] = lambda: False,
                  isTargetAmp:typing.Callable[[],bool] = lambda: False,
                  useAutoStart:typing.Callable[[],bool] = lambda: True
                ):
        self.isIndexerReady = isIndexerReady
        self.getDistance = getDistance
        self.isTargetAmp = isTargetAmp
        self.useAutoStart = useAutoStart

        super().__init__(
            {
                "speaker": LauncherSpeaker( launcher, getDistance ),
                "amp": LauncherAmp( launcher ),
                "toss": LauncherToss( launcher ),
                "wait": commands2.cmd.none().withName("LauncherWait")
            },
            self.getState
        )

    def getState(self):
        if not self.isIndexerReady() or not self.useAutoStart():
            return "wait"
        elif self.isTargetAmp():
            return "amp"
        elif self.getDistance() < Launcher.LauncherSpeeds.SpeakerDistanceHigh.get():
            return "speaker"
        else:
            return "toss"

    def initialize(self):
        super().initialize()
        self.setName( self._selectedCommand.getName() )
        