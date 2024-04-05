from commands2 import ParallelCommandGroup

from commands import *
from util import *

from subsystems import Intake, Indexer, Pivot

class NoteToss(ParallelCommandGroup):
    def __init__(self, indexer:Indexer, launcher:Launcher, pivot:Pivot):
        super().__init__(
            PivotToss(pivot),
            LauncherToss(launcher),
            IndexerLaunch(indexer, lambda: launcher.atSpeed(300) and pivot.atPositionToss() )
        )
        self.setName( "NoteToss" )
