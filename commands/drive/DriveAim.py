import typing

from commands2 import SelectCommand
import commands2.cmd

from commands.drive.DriveAimAmp import DriveAimAmp
from commands.drive.DriveAimSpeaker import DriveAimSpeaker
from subsystems import SwerveDrive
from util import LaunchCalc

class DriveAim(SelectCommand):
    def __init__( self,
                  swerveDrive:SwerveDrive,
                  velocityX:typing.Callable[[], float],
                  velocityY:typing.Callable[[], float],
                  getTarget:typing.Callable[[], LaunchCalc.Targets]
                ):
        self.getTarget = getTarget
        super().__init__(
            {
                LaunchCalc.Targets.SPEAKER: DriveAimSpeaker(
                    swerveDrive,
                    velocityX,
                    velocityY
                ),
                LaunchCalc.Targets.AMP: DriveAimAmp(
                    swerveDrive,
                    velocityX,
                    velocityY
                ),
                None: commands2.cmd.none(),
            },
            getTarget
        )

    def getTargetFunction(self):
        match self.getTarget():
            case LaunchCalc.Targets.SPEAKER:
                return "Speaker"
            case LaunchCalc.Targets.AMP:
                return "Amp"
            case _:
                return "None"

    def initialize(self):
        # Write New Name
        self.setName( self._selectedCommand.getName() )
        super().initialize()