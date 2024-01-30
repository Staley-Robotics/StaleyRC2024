import commands2
from subsystems.intake import Intake

class IntakeMidPosition(commands2.Command):
    def __init__(self, intake: Intake):
        super().__init__()
        self.intake = intake
        self.addRequirements(intake)
        self.setName("IntakeMidPosition")

    def execute(self):
        if self.intake.getFrontIR():
            self.intake.setTargetVel(1)
        elif self.intake.getBackIR():
            self.intake.setTargetVel(-1)

    def isFinished(self) -> bool:
        return (self.intake.getFrontIR() and self.intake.getBackIR())

    def end(self, interrupted:bool):
        pass
        

class IntakeEject(commands2.Command):
    def __init__(self, intake: Intake):
        super().__init__()
        self.intake = intake
        self.addRequirements(intake)
        self.setName("IntakeEject")

    def execute(self):
        if self.intake.getBackIR() or self.intake.getFrontIR():
            self.intake.setTargetVel(-1)
    
    def isFinished(self):
        return not self.intake.getFrontIR() or self.intake.getBackIR()

    def end(self, interrupted:bool):
        pass


