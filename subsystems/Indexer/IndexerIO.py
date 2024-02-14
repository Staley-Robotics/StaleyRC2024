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

    def __init__(self):
        pass

    def updateInputs(self, inputs:IndexerIOInputs) -> None:
        pass

    def run(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def setBrake(self, brake:bool) -> None:
        pass

    def setVelocity(self, velocity:float) -> None:
        pass

    def getVelocity(self) -> float:
        pass

    def atSetpoint(self) -> bool:
        pass
    
    def getSetpoint(self) -> bool:
        pass
