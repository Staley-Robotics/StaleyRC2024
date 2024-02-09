import commands2

from subsystems import *

class PointPivotToAngle(commands2.Command):
    def __init__(self, pivot: ShooterPivot, getLeftY):
        super().__init__()
        self.pivot = pivot
        self.position = 0.5
    
    def initialize(self):
        super().initialize()
    
    def execute(self):
        super().execute()
        self.pivot.go_to()
    
    def end(self, interrupted: bool):
        super().end(interrupted)
        self.intake.stop()