import typing

from commands2 import SelectCommand
import commands2.cmd
from wpilib import RobotState

from commands import IntakeHandoff, IntakeLoad
from subsystems import Intake

class IntakeDefault(SelectCommand):
    def __init__( self,
                  intake:Intake,
                  indexerHasNote:typing.Callable[[],bool],
                  pivotAtHandoff:typing.Callable[[],bool],
                  useAutoStart:typing.Callable[[],bool]
                ):
        self.intake = intake
        self.indexerHasNote = indexerHasNote
        self.pivotAtPosition = pivotAtHandoff
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
        elif self.intake.hasNote():
            if self.pivotAtPosition():
                return "handoff"
            else:
                return "wait"
        elif RobotState.isAutonomous():
            return "load"
        else:
            return "wait"

    def initialize(self):
        super().initialize()
        self.setName( self._selectedCommand.getName() )
        