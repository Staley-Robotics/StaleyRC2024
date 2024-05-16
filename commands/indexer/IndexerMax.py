### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems import Indexer
from util import *

# Intake Load Command
class IndexerMax(Command):
    def __init__( self,
                  indexer:Indexer
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        
        self.indexer = indexer
        self.setName( "IndexerMax" )
        self.addRequirements( indexer )

    def initialize(self) -> None:
        self.indexer.setBrake(False)

    def execute(self) -> None:
        self.indexer.set(Indexer.IndexerSpeeds.Max.get())

    def end(self, interrupted:bool) -> None:
        self.indexer.set(Indexer.IndexerSpeeds.Stop.get())

    def isFinished(self) -> bool:
        return False
    
    def runsWhenDisabled(self) -> bool: return False
    