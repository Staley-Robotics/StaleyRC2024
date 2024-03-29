from commands2 import SelectCommand
import commands2.cmd
from wpilib import RobotState

from subsystems import Led2
from commands import LedCelebration, LedDistraction

class LedAction(SelectCommand):
    def __init__(self, led:Led2):
        super().__init__(
            {
                "Celebration": LedCelebration( led ),
                "Distraction": LedDistraction( led ),
                "None": commands2.cmd.none().withName("NoLeds")
            },
            self.actionSelect
        )
        self.setName( "LedAction" )

    def actionSelect(self):
        if RobotState.isDisabled():
            return "Celebration"
        elif RobotState.isTeleop():
            return "Distraction"
        else:
            return "None"

    def initialize(self):
        super().initialize()
        self.setName( self._selectedCommand.getName() )

    def end(self, interrupted:bool):
        super().end(interrupted)
        self.setName( "LedAction" )

    def runsWhenDisabled(self):
        return True
