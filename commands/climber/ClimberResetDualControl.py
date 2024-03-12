from commands2 import Command

from subsystems import Climber
from util import *
"""
NOTE: unfinsihed idk wahtes happeningitb heree
"""
class ClimberResetDualControl(Command):
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

        self.lStalledCycleCount = 0
        self.rStalledCycleCount = 0
        self.lastLPosition = self.climber.getLPosition()
        self.lastRPosition = self.climber.getRPosition()
        self.climber.setLPosition( self.resetPosition )
        self.climber.setRPosition( self.resetPosition )

    def execute(self) -> None:
        lPos, rPos = self.climber.getLPosition(), self.climber.getRPosition()
        # Left
        difference = lPos - self.lastLPosition
        if abs( difference ) < self.positionThreshold:
            self.lStallCycleCount += 1
        else:
            self.lStallCycleCount = 0
        self.lastLPosition = lPos
        self.climber.updateLeft()
        # Right
        difference = rPos - self.lastRPosition
        if abs( difference ) < self.positionThreshold:
            self.rStallCycleCount += 1
        else:
            self.rStallCycleCount = 0
        self.lastRPosition = rPos
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
