import commands2

from commands import *

from subsystems import Intake, Indexer

class Handoff(commands2.ParralelCommandGroup):
    def __init__(self, intake:Intake, indexer:Indexer):
        super().__init__()

        self.addCommands(
            IntakeHandoff(intake),
            IndexerHandoff(indexer)
        )