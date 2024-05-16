# FRC
from commands2 import Command
from util.LaunchCalc import LaunchCalc

class ToggleClimb(Command):
    def __init__(self, launchCalc:LaunchCalc ):
        super().__init__()
        self.launchCalc = launchCalc
        pass

    def initialize(self):
        if self.launchCalc.isTargetTrap():
            self.launchCalc.setTarget( LaunchCalc.Targets.SPEAKER )
        else:
            self.launchCalc.setTarget( LaunchCalc.Targets.CLIMB )

    def isFinished(self) -> bool:
        return True

    def runsWhenDisabled(self) -> bool:
        return True