from commands2 import Command

from subsystems import Climber
from util import *
"""
NOTE: unfinsihed idk wahtes happeningitb heree
"""
class ClimberReset(Command):
    def __init__( self,
                  climber:Climber,
                  positionThreshold: float = 100.0,
                  timerThreshold: float = 2.0,
                  stalledCycleThreshold: float = 5
                ):
        # CommandBase Initiation Configurations
        self.climber = climber

        self.timer = Timer()
        self.lStalledCycleCount = 0
        self.rStalledCycleCount = 0
        self.lastPosition = self.climber.getPosition()

        # Consts -- probably gonna be different than this format
        self.positionThreshold = positionThreshold
        self.timerThreshold = timerThreshold
        self.stalledCycleThreshold = stalledCycleThreshold

        # Command setup
        self.setName( "ClimberReset" )
        self.addRequirements( climber )

    def initialize(self) -> None:
        self.timer.reset()
        self.timer.start()

        self.stalledCycleCount = [ 0, 0 ]
        self.lastPosition = self.climber.getPosition()

    def execute(self) -> None:
        self.climber.set(
            Climber.ClimberPositions.Reset.get(),
            Climber.ClimberPositions.Reset.get(),
            override = True
        )

        currentPos = self.climber.getPosition()
        
        # Loop Through Motors
        for i in range(len(self.stalledCycleCount)):
            diff = currentPos[i] - self.lastPosition[i]
            if abs( diff ) < self.positionThreshold:
                self.stalledCycleCount[i] += 1
            else:
                self.stalledCycleCount[i] = 0

        self.lastPosition = currentPos

    def end(self, interrupted:bool) -> None:
        # Stop Timer
        self.timer.stop()

        # Stop Climber
        self.climber.reset()
        self.climber.stop()

    def isFinished(self) -> bool:
        if self.timer.get() < self.timerThreshold:
            isStalled = True
            for i in range(len(self.stalledCycleCount)):
                isStalled = isStalled and self.stalledCycleCount[i] >= self.stalledCycleThreshold
            return isStalled
        else:
            return True
    
    def runsWhenDisabled(self) -> bool: return False
