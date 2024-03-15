from commands2 import Command

from subsystems import Climber
from util import *
"""
NOTE: unfinsihed idk wahtes happeningitb heree
"""
class ClimberResetSwitch(Command):
    def __init__( self,
                  climber:Climber,
                  positionThreshold: float = 100.0,
                  timerThreshold: float = 2.0,
                  stalledCycleThreshold: float = 5
                ):
        # CommandBase Initiation Configurations
        self.climber = climber

        # Command setup
        self.setName( "ClimberResetSwitch" )
        self.addRequirements( climber )

    def initialize(self) -> None:
        pass

    def execute(self) -> None:
        self.climber.set(
            Climber.ClimberPositions.Reset.get(),
            Climber.ClimberPositions.Reset.get(),
            override = True
        )

    def end(self, interrupted:bool) -> None:
        self.climber.stop()

    def isFinished(self) -> bool:
        return self.climber.atBottom()
    
    def runsWhenDisabled(self) -> bool: return False
