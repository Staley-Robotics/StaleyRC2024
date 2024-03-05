import commands2

from commands import *
from util import *

from subsystems import Intake, Indexer, Pivot

class NoteLaunchTrap(commands2.SequentialCommandGroup):
    def __init__(self, indexer:Indexer, launcher:Launcher, pivot:Pivot, elevator:Elevator):
        super().__init__()
        self.setName( "TrapLaunch" )

        self.addCommands(
            commands2.ParallelCommandGroup(
                ElevatorTrap(elevator)
            )
        )
        self.addCommands(
            commands2.ParallelRaceGroup(
                PivotTrap(pivot),
                commands2.ParallelCommandGroup(
                    LauncherTrap(launcher),
                    commands2.SequentialCommandGroup(
                        commands2.WaitCommand( 0.025 ),
                        commands2.WaitUntilCommand( condition = launcher.atSpeed ),
                        IndexerLaunch(indexer)
                    )
                )
            )
        )
