### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems import Indexer
from util import *

# Intake Load Command
class IndexerHandoff(Command):
    def __init__( self,
                  indexer:Indexer
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.indexer = indexer

        self.setName( "IndexerHandoff" )
        self.addRequirements( indexer )

    def initialize(self) -> None:
        self.indexer.setBrake(True)

    def execute(self) -> None:
        self.indexer.set(Indexer.IndexerSpeeds.Handoff)
    
    def end(self, interrupted:bool) -> None:
        self.indexer.set(Indexer.IndexerSpeeds.Stop)

    def isFinished(self) -> bool: 
        return self.indexer.hasNote()
    
    def runsWhenDisabled(self) -> bool: return False
