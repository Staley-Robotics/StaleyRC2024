import commands2

from commands import *
from util import *

from subsystems import Intake, Indexer, Pivot, Elevator

class NoteLoadSource(commands2.SequentialCommandGroup):
    def __init__(self, indexer:Indexer, pivot:Pivot, elevator:Elevator, launcher:Launcher):
        super().__init__()
        self.setName( "SourceLoad" )

        self.addCommands(
            commands2.ParallelCommandGroup(
                ElevatorSource(elevator),
                PivotSource(pivot)
            )
        )
        self.addCommands(
            commands2.ParallelCommandGroup(
                LauncherSource(launcher),
                IndexerSource(indexer)
            )
        )
        self.addCommands(
            commands2.ParallelCommandGroup(
                ElevatorBottom(elevator),
                #PivotHandoff(pivot) # Do we need this if AutoAim should take over?
            )
        )