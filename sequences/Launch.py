import commands2

from commands import *

from util import *

from subsystems import Intake, Indexer

class Handoff(commands2.SequentialCommandGroup):
    def __init__(self, intake:Intake, indexer:Indexer):
        super().__init__()

        self.addCommands(
            IntakeHandoff(intake).withTimeout(0.5),
            IndexerHandoff(indexer)
        )