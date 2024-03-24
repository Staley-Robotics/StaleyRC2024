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
        sensorTop: bool = True
        sensorBottom: bool = True

    def __init__(self):
        pass

    def updateInputs(self, inputs:ClimberIOInputs) -> None:
        pass

    def run(self) -> None:
        pass

    def setBrake(self, brake:bool) -> None:
        pass

    def setRate(self, rate:float) -> None:
        pass

    def getRate(self) -> float:
        return 0.0

    def getSetpoint(self) -> float:
        return 0.0
    
    def atTop(self) -> bool:
        return False
    
    def atBottom(self) -> bool:
        return False