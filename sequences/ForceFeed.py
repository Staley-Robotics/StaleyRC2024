import commands2

from commands import *

from util import *

from subsystems import Intake, Indexer, Launcher, Pivot

class ForceFeed(commands2.ParallelDeadlineGroup):
    def __init__(self, intake:Intake, indexer:Indexer, launcher:Launcher, pivot:Pivot):
        super().__init__(
            commands2.cmd.waitSeconds( 5.0 ),
            IntakeMax(intake),
            PivotHandoff(pivot),
            IndexerMax(indexer),
            LauncherStop(launcher)
        )