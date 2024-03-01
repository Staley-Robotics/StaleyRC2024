import commands2

from commands import *
from util import *

from subsystems import Intake, Indexer, Pivot, Elevator

class NoteLoadGround(commands2.SequentialCommandGroup):
    def __init__(self, intake:Intake, indexer:Indexer, pivot:Pivot, elevator:Elevator):
        super().__init__()
        self.setName( "NoteLoadGround" )

        self.addCommands(
            commands2.ParallelCommandGroup(
                IntakeLoad(intake),
                PivotHandoff(pivot),
                #ElevatorBottom(elevator)
            )
        )
        self.addCommands(
            commands2.ParallelCommandGroup(
                IntakeHandoff(intake),
                IndexerHandoff(indexer)
            )
        )