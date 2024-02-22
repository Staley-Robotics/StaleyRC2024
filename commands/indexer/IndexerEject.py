### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command
from wpilib import Timer

# Our Imports
from subsystems import Indexer
from util import *

# Intake Load Command
class IndexerEject(Command):
    def __init__( self,
                  indexer:Indexer,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.timer = Timer()
        self.indexer = indexer

        self.setName( "IndexerEject" )
        self.addRequirements( indexer )

    def initialize(self) -> None:
        self.timer.reset()
        self.timer.start()
        self.indexer.setBrake(False)

    def execute(self) -> None:
        self.indexer.set(Indexer.IndexerSpeeds.Eject.get())

    def end(self, interrupted:bool) -> None:
        self.timer.stop()
        self.indexer.set(Indexer.IndexerSpeeds.Stop.get())

    def isFinished(self) -> bool:
        return self.timer.hasElapsed(2.0)
    
    def runsWhenDisabled(self) -> bool: return False

    def cancel(self) -> None:
        return super().cancel()