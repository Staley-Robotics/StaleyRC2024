import typing

from commands2 import SelectCommand
import commands2.cmd
from wpilib import RobotBase

from commands import IndexerHandoff, IndexerLoad, IndexerLaunch, IndexerSafeHandoff
from subsystems import Indexer

class IndexerDefault(SelectCommand):
    def __init__( self,
                  indexer: Indexer,
                  intakeHasNote: typing.Callable[[], bool],
                  pivotAtHandoff: typing.Callable[[], bool],
                  isLaunchApproved: typing.Callable[[], bool] = lambda: False
                ):
        self.indexer = indexer
        self.intakeHasNote = intakeHasNote
        self.pivotAtPosition = pivotAtHandoff
        self.useAutoLaunch = isLaunchApproved

        super().__init__(
            {
                "handoff": IndexerHandoff(indexer),
                "safehandoff": IndexerSafeHandoff(indexer, self.intakeHasNote ),
                "load": IndexerLoad(indexer),
                "launch": IndexerLaunch(indexer, lambda:True),
                "wait": commands2.cmd.none().withName("IndexerWait"),
            },
            self.getState,
        )

    def getState(self) -> str:
        if self.indexer.hasNote() and self.useAutoLaunch():
            return "launch"
        elif self.intakeHasNote() and self.pivotAtPosition():
            if RobotBase.isAutonomous():
                return "safehandoff"
            return "handoff"
        elif self.indexer.hasHalfNote() != 0:
            return "load"
        else:
            return "wait"

    def initialize(self):
        super().initialize()
        self.setName(self._selectedCommand.getName())
