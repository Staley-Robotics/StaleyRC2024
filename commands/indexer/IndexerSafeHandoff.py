### Imports
# Python Imports
import typing

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems import Indexer
from util import *

# Intake Load Command
class IndexerSafeHandoff(Command):
    def __init__( self,
                  indexer:Indexer,
                  intakeHasNote:typing.Callable[[],bool]
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.indexer = indexer
        self.intakeHasNote = intakeHasNote()

        self.setName( "IndexerHandoff" )
        self.addRequirements( indexer )

    def initialize(self) -> None:
        self.indexer.setBrake(True)

    def execute(self) -> None:
        self.indexer.set(Indexer.IndexerSpeeds.Handoff.get())
    
    def end(self, interrupted:bool) -> None:
        self.indexer.set(Indexer.IndexerSpeeds.Stop.get())

    def isFinished(self) -> bool: 
        return self.indexer.hasNote() and not self.intakeHasNote()
    
    def runsWhenDisabled(self) -> bool: return False
