### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems.Indexer import Indexer
from util import *

# Intake Load Command
class IndexerLaunch(Command):
    def __init__( self,
                  indexer:Intake,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.indexer = indexer

        self.setName( "IndexerLaunch" )
        self.addRequirements( indexer )

    def initialize(self) -> None:
        self.indexer.setBrake(False)

    def execute(self) -> None:
        self.indexer.set(Indexer.IndexerSpeeds.Launch)

    def end(self, interrupted:bool) -> None:
        self.indexer.set(Indexer.IndexerSpeeds.Stop)

    def isFinished(self) -> bool:
        return not self.indexer.hasNote()
    
    def runsWhenDisabled(self) -> bool: return False
