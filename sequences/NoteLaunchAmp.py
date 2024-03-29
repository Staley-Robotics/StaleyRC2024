import commands2

from commands import *
from util import *

from subsystems import Intake, Indexer, Pivot

class NoteLaunchAmp(commands2.SequentialCommandGroup):
    def __init__(self, indexer:Indexer, launcher:Launcher, pivot:Pivot):
        super().__init__()
        self.setName( "AmpLaunch" )

        self.addCommands(
            commands2.ParallelCommandGroup(
                PivotAmp(pivot),
                commands2.ParallelCommandGroup(
                    LauncherAmp(launcher),
                    commands2.SequentialCommandGroup(
                        commands2.WaitCommand( 0.025 ),
                        commands2.WaitUntilCommand( condition = lambda: launcher.atSpeed(300) ),
                        IndexerLaunch(indexer)
                    )
                )
            )
        )
