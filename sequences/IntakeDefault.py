import commands2

from commands import *
from subsystems import Intake
from util import *

class IntakeDefault(commands2.SelectCommand):
    def __init__( self,
                  intake:Intake,
                  indexerHasNote:typing.Callable[[],bool],
                  pivotAtPosition:typing.Callable[[],bool],
                  useAutoStart:typing.Callable[[],bool]
                ):
        self.intake = intake
        self.indexerHasNote = indexerHasNote
        self.pivotAtPosition = pivotAtPosition
        self.useAutoStart = useAutoStart

        super().__init__(
            {
                "handoff": IntakeHandoff(intake),
                "load": IntakeLoad(intake),
                "wait": commands2.cmd.none().withName("IntakeWait")
            },
            self.getState
        )

    def getState(self) -> str:
        if self.useAutoStart() and self.intake.foundNote() and not self.indexerHasNote() and not self.intake.hasNote():
            return "load"
        elif self.intake.hasNote() and self.pivotAtPosition():
            return "handoff"
        else:
            return "wait"

    def initialize(self):
        super().initialize()
        self.setName( self._selectedCommand.getName() )
        