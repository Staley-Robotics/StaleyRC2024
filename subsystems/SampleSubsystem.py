import commands2

class SampleSubsystem(commands2.SubsystemBase):
    def __init__(self):
        super().__init__()

    def periodic(self) -> None:
        return super().periodic()
    
    def simulationPeriodic(self) -> None:
        return super().simulationPeriodic()