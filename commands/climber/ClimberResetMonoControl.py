from commands2 import Command

from subsystems import Climber
from util import *

class ClimberResetMonoControl(Command):
    def __init__( self,
                  climber:Climber,
                  resetPosition: float,
                  positionThreshold: float,
                  timerThreshold: float,
                  stalledCycleThreshold: float
                ):
        # CommandBase Initiation Configurations
        self.climber = climber

        self.timer = Timer()
        self.stalledCycleCount = 0
        self.lastPositions = (0,0)

        # Consts -- probably gonna be different than this format
        self.resetPosition = resetPosition
        self.positionThreshold = positionThreshold
        self.timerThreshold = timerThreshold
        self.stalledCycleThreshold = stalledCycleThreshold

        # Command setup
        self.setName( "ClimberReset" )
        self.addRequirements( climber )

    def initialize(self) -> None:
        self.timer.reset()
        self.timer.start()
        self.stalledCycleCount = 0
        self.lastPositions = self.climber.getLPosition(), self.climber.getRPosition()
        self.climber.setLPositions(self.resetPosition)
        self.climber.setRPositions(self.resetPosition)

    def execute(self) -> None:
        currentPositions = self.climber.getLPosition(), self.climber.getRPosition()
        for i, pos in enumerate(currentPositions):
            difference = pos - self.lastPositions[i]
            if abs( difference ) < self.positionThreshold:
                self.stallCycleCount += 1
            else:
                self.stallCycleCount = 0
        
        self.lastPositions = currentPositions
        self.climber.updateLeft()
        self.climber.updateRight()

    def end(self, interrupted:bool) -> None:
        self.timer.stop()
        #I dunno, copied from armExtend
        # #if not interrupted:
        # self.climber.resetPosition()
        # self.climber.update()

    def isFinished(self) -> bool:
        if self.timer.get() < self.timerThreshold:
            return self.stalledCycleCount >= self.stalledCycleThreshold
        else:
            return True
    
    def runsWhenDisabled(self) -> bool: return False
