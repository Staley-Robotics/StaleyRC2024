### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems import Indexer
from util import *

# Intake Load Command
class IndexerDefault(Command):
    def __init__( self,
                  indexer:Indexer
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.indexer = indexer

        self.setName( "IndexerDefault" )
        self.addRequirements( indexer )

    def initialize(self) -> None:
        self.indexer.setBrake(True)

    def execute(self) -> None:
        halfNote = self.indexer.hasHalfNote()
        if halfNote == 1:
            self.indexer.set( Indexer.IndexerSpeeds.SelfIn.get() )
        elif halfNote == -1:
            self.indexer.set( Indexer.IndexerSpeeds.SelfOut.get() )
    
    def end(self, interrupted:bool) -> None:
        self.indexer.set( Indexer.IndexerSpeeds.Stop.get() )

    def isFinished(self) -> bool: 
        return self.indexer.hasHalfNote() == 0
    
    def runsWhenDisabled(self) -> bool: return False
