import dataclasses

import wpiutil.wpistruct

class IndexerIO:

    @wpiutil.wpistruct.make_wpistruct(name="IndexerIOInputs")
    @dataclasses.dataclass
    class IndexerIOInputs:
        position: float = 0
        velocity: float = 0
        appliedVolts: float = 0
        currentAmps: float = 0
        tempCelcius: float = 0

        sensorHandoff:bool = False
        sensorLaunch:bool = False

    def __init__(self):
        pass

    def updateInputs(self, inputs:IndexerIOInputs) -> None:
        pass

    def run(self) -> None:
        pass

    def setBrake(self, brake:bool) -> None:
        pass

    def setVelocity(self, velocity:float) -> None:
        pass

    def getVelocity(self) -> float:
        return 0.0

    def atSetpoint(self, errorRange:float=0.0) -> bool:
        sp = self.getSetpoint()
        veloc = self.getVelocity()
        atSpeed = abs( sp - veloc ) < errorRange
        return atSpeed
    
    def getSetpoint(self) -> bool:
        return 0.0
