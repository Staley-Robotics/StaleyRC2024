import commands2

from subsystems import *

class RunIntake(commands2.Command):
    def __init__(self, intake: Intake):
        super().__init__()
        self.intake = intake
    
    def initialize(self):
        super().initialize()
        self.intake.setTargetVel(self.intake.runVel.get() * (-1 if reversed else 1))
    
    def execute(self):
        return super().execute()
    
    def end(self, interrupted: bool):
        super().end(interrupted)
        self.intake.setTargetVel(0)

class RunIntakeReversed(commands2.Command):
    def __init__(self, intake: Intake):
        super().__init__()
        self.intake = intake
    
    def initialize(self):
        super().initialize()
        self.intake.run(True)
    
    def execute(self):
        return super().execute()
    
    def end(self, interrupted: bool):
        super().end(interrupted)
        self.intake.stop()

