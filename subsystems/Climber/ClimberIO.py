import dataclasses

import wpiutil.wpistruct

class ClimberIO:

    @wpiutil.wpistruct.make_wpistruct(name="ClimberIOInputs")
    @dataclasses.dataclass
    class ClimberIOInputs:
        #Motor
        motorAppliedVolts: float = 0.0
        motorCurrentAmps: float = 0.0
        motorTempCelcius: float = 0.0
        motorVelocity: float = 0.0
        motorPosition: float = 0.0
        sensor: bool = True

    def __init__(self):
        pass

    def updateInputs(self, inputs:ClimberIOInputs) -> None:
        pass

    def run(self) -> None:
        pass

    def setBrake(self, brake:bool) -> None:
        pass

    def setPosition(self, position:float) -> None:
        pass

    def movePosition(self, rate:float) -> None:
        pass

    def resetPosition(self, position:float) -> None:
        pass

    def getPosition(self) -> float:
        return 0.0

    def atSetpoint(self, errorRange:float = 100.0) -> bool:
        leftPos = self.getPosition()
        leftSp = self.getSetpoint()
        leftAtPos = abs( leftSp - leftPos ) < errorRange
        return leftAtPos
    
    def getSetpoint(self) -> float:
        return 0.0
    
