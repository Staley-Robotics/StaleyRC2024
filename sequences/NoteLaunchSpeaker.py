import commands2

from commands import *
from subsystems import Indexer, Pivot, Elevator, Launcher
from util import *

class NoteLaunchSpeaker(commands2.SequentialCommandGroup):
    def __init__(self, indexer:Indexer, launcher:Launcher, pivot:Pivot, elevator:Elevator, getPose:typing.Callable[[],Pose2d]):
        super().__init__()
        self.setName( "NoteLaunchSpeaker" )

        self.addCommands(
            commands2.ParallelCommandGroup(
                ElevatorBottom(elevator)
            )
        )
        self.addCommands(
            commands2.ParallelRaceGroup(
                commands2.RepeatCommand(
                    PivotAim(pivot,getPose)
                ),
                commands2.ParallelCommandGroup(
                    LauncherSpeaker(launcher),
                    commands2.SequentialCommandGroup(
                        commands2.WaitCommand( 0.025 ),
                        commands2.WaitUntilCommand( condition = launcher.atSpeed ),
                        IndexerLaunch(indexer)
                    )
                )
            )
        )
