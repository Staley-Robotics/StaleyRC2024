from wpilib.simulation import ElevatorSim
from wpimath.system.plant import DCMotor

from .ElevatorIO import ElevatorIO

class ElevatorIOSim(ElevatorIO):
    def __init__(self):
        self.elevator = ElevatorSim(
            gearbox = DCMotor.NEO(2),
            gearing = 1.0,
            carriageMass = 0.1,
            drumRadius = 0.1,
            minHeight = 0,
            maxHeight = 1.0,
            simulateGravity = True,
            startingHeight = 0
        )
    pass

    def updateInputs(self, inputs:ElevatorIO.ElevatorIOInputs):
        self.elevator.update(0.02)

    def run(self):
        self.elevator.setInputVoltage()