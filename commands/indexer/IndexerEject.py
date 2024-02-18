### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command
from wpilib import Timer

# Our Imports
from subsystems.Indexer import Indexer
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

    def initialize(self) -> None:
        self.timer.reset()
        self.timer.start()
        self.indexer.setBrake(False)

    def execute(self) -> None:
        self.indexer.set(Intake.IntakeSpeeds.Eject)

    def end(self, interrupted:bool) -> None:
        self.timer.stop()
        self.indexer.set(Intake.IntakeSpeeds.Stop)

    def isFinished(self) -> bool:
        return self.timer.hasElapsed(2.0)
    
    def runsWhenDisabled(self) -> bool: return False
