import commands2

from commands import *
from util import *

from subsystems import Intake, Indexer, Pivot

class NoteToss(commands2.SequentialCommandGroup):
    def __init__(self, indexer:Indexer, launcher:Launcher, pivot:Pivot, elevator:Elevator):
        super().__init__()
        self.setName( "NoteToss" )

        self.addCommands(
            commands2.ParallelCommandGroup(
                ElevatorAmp(elevator)
            )
        )
        self.addCommands(
            PivotToss(pivot),
        )
        self.addCommands(
            commands2.ParallelCommandGroup(
                LauncherToss(launcher),
                commands2.SequentialCommandGroup(
                    commands2.WaitCommand( 0.025 ),
                    commands2.WaitUntilCommand( condition = lambda: launcher.atSpeed(300) ),
                    IndexerLaunch(indexer)
                )
            )
        )
