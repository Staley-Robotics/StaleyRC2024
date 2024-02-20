import dataclasses

import wpiutil.wpistruct

class ElevatorIO:

    @wpiutil.wpistruct.make_wpistruct(name="ElevatorIOInputs")
    @dataclasses.dataclass
    class ElevatorIOInputs:
        leftPosition: float = 0
        leftVelocity: float = 0
        leftAppliedVolts: float = 0
        leftCurrentAmps: float = 0
        leftTempCelcius: float = 0

        rightPosition: float = 0
        rightVelocity: float = 0
        rightAppliedVolts: float = 0
        rightCurrentAmps: float = 0
        rightTempCelcius: float = 0

    def __init__(self):
        pass

    def updateInputs(self, inputs:ElevatorIOInputs) -> None:
        pass

    def run(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def setPosition(self, position) -> None:
        pass

    def movePosition(self, input) -> None:
        pass

    def getPosition(self) -> float:
        pass

    def atSetpoint(self) -> bool:
        pass
    
    def getSetpoint(self) -> float:
        pass