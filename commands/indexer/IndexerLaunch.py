### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command, WaitUntilCommand

# Our Imports
from subsystems import Indexer
from util import *

# Intake Load Command
class IndexerLaunch(WaitUntilCommand):
    def __init__( self,
                  indexer:Indexer,
                  launcherAtSpeed:typing.Callable[[],bool]
                ):
        # CommandBase Initiation Configurations
        super().__init__( launcherAtSpeed )
        
        self.indexer = indexer
        self.setName( "IndexerLaunch" )
        self.addRequirements( indexer )

    def initialize(self) -> None:
        super().initialize()
        self.indexer.setBrake(False)

    def execute(self) -> None:
        super().execute()
        self.indexer.set(Indexer.IndexerSpeeds.Launch.get())

    def end(self, interrupted:bool) -> None:
        super().end()
        self.indexer.set(Indexer.IndexerSpeeds.Stop.get())

    def isFinished(self) -> bool:
        return self.indexer.hasReleasedNote()
    
    def runsWhenDisabled(self) -> bool: return False
    