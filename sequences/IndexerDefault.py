import commands2

from commands import *
from subsystems import Indexer
from util import *


class IndexerDefault(commands2.SelectCommand):
    def __init__( self,
                  indexer: Indexer,
                  intakeHasNote: typing.Callable[[], bool],
                  pivotAtPosition: typing.Callable[[], bool],
                  isLaunchApproved: typing.Callable[[], bool] = lambda: False
                ):
        self.indexer = indexer
        self.intakeHasNote = intakeHasNote
        self.pivotAtPosition = pivotAtPosition
        self.useAutoLaunch = isLaunchApproved

        super().__init__(
            {
                "handoff": IndexerHandoff(indexer),
                "load": IndexerLoad(indexer),
                "launch": IndexerLaunch(indexer),
                "wait": commands2.cmd.none().withName("IndexerWait"),
            },
            self.getState,
        )

    def getState(self) -> str:
        if self.indexer.hasNote() and self.useAutoLaunch():
            return "launch"
        elif self.intakeHasNote() and self.pivotAtPosition():
            return "handoff"
        elif self.indexer.hasHalfNote() != 0:
            return "load"
        else:
            return "wait"

    def initialize(self):
        super().initialize()
        self.setName(self._selectedCommand.getName())
