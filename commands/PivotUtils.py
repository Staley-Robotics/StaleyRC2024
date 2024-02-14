import typing

import commands2

from subsystems import *

class PointPivotToAngle(commands2.Command):
    def __init__(self, pivot: ShooterPivot, getPosY: typing.Callable=lambda:0.0, getNegativeY: typing.Callable=lambda:0.0):
        super().__init__()
        self.addRequirements(pivot)
        self.pivot = pivot
        self.position = 0.5
        self.getPosSpeed = getPosY
        self.getNegativeSpeed = getNegativeY
    
    def initialize(self):
        super().initialize()
    
    def execute(self):
        super().execute()
        self.pivot.set_speed(self.getPosSpeed() - self.getNegativeSpeed())
    
    def end(self, interrupted: bool):
        super().end(interrupted)
        self.pivot.set_speed(0)