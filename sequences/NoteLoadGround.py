import commands2

from commands import *
from util import *

from subsystems import Intake, Indexer, Pivot

class NoteLoadGround(commands2.SequentialCommandGroup):
    def __init__(self, intake:Intake, indexer:Indexer, pivot:Pivot):
        super().__init__()
        self.setName( "NoteLoadGround" )

        self.addCommands(
            PivotHandoff(pivot)
        )
        self.addCommands(
            commands2.ParallelDeadlineGroup(
                IndexerHandoff(indexer),
                IntakeHandoff(intake),
            )
        )
        self.addCommands(
            IndexerLoad( indexer )
        )