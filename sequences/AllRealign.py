import commands2

from commands import *
from subsystems import Intake, Indexer, Launcher, Pivot


class AllRealign(commands2.ParallelCommandGroup):
    def __init__(self, intake:Intake, indexer:Indexer, launcher:Launcher, pivot:Pivot):
        super().__init__(
            commands2.SequentialCommandGroup(
                PivotHandoff(pivot),
                commands2.ParallelCommandGroup(   
                    IntakeHandoff(intake),
                    IndexerRealign(indexer)
                )
            ),
            LauncherStop(launcher)
        )
        self.setName( "Realign!" )