import commands2

from commands import *
from util import *

from subsystems import Intake, Indexer, Pivot

class NoteLoadSource(commands2.SequentialCommandGroup):
    def __init__(self, indexer:Indexer, pivot:Pivot, launcher:Launcher):
        super().__init__()
        self.setName( "SourceLoad" )

        self.addCommands(
            commands2.ParallelCommandGroup(
                PivotSource(pivot)
            )
        )
        self.addCommands(
            commands2.ParallelCommandGroup(
                LauncherSource(launcher),
                IndexerSource(indexer)
            )
        )
