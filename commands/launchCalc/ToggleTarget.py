# FRC
from commands2 import Command
from util.LaunchCalc import LaunchCalc

class ToggleTarget(Command):
    def __init__(self, launchCalc:LaunchCalc ):
        super().__init__()
        self.launchCalc = launchCalc
        pass

    def initialize(self):
        match self.launchCalc.getTarget():
            case LaunchCalc.Targets.SPEAKER:
                self.launchCalc.setTarget( LaunchCalc.Targets.AMP )
            case LaunchCalc.Targets.AMP:
                self.launchCalc.setTarget( LaunchCalc.Targets.SPEAKER )
            case _:
                pass

    def isFinished(self) -> bool:
        return True

    def runsWhenDisabled(self) -> bool:
        return True