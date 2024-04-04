import commands2

from commands import *
from subsystems import Indexer, Pivot, Launcher
from util import *

class NoteLaunchSpeaker(commands2.SequentialCommandGroup):
    def __init__(self, indexer:Indexer, launcher:Launcher, pivot:Pivot, launchCalc:LaunchCalc):
        super().__init__()
        self.setName( "NoteLaunchSpeaker" )
        self.addRequirements(
            indexer, launcher, pivot
        )

        self.addCommands(
            commands2.ParallelRaceGroup(
                commands2.RepeatCommand(
                    PivotAim(pivot,launchCalc.getLaunchAngle)
                ),
                commands2.ParallelCommandGroup(
                    LauncherSpeaker(launcher, launchCalc.getDistance),
                    commands2.SequentialCommandGroup(
                        commands2.WaitCommand( 0.025 ),
                        IndexerLaunch(indexer,  launcher.atSpeed)
                    )
                )
            )
        )
