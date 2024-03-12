import dataclasses

import wpiutil.wpistruct

class PivotIO:

    @wpiutil.wpistruct.make_wpistruct(name="PivotIOInputs")
    @dataclasses.dataclass
    class PivotIOInputs:
        motorPosition: float = 0.0
        motorVelocity: float = 0.0
        motorAppliedVolts: float = 0.0
        motorCurrentAmps: float = 0.0
        motorTempCelcius: float = 0.0

        encoderPositionAbs: float = 0.0
        encoderPositionRel: float = 0.0
        encoderVelocity: float = 0.0

        setPosition: float = 0.0

    def __init__(self):
        pass

    def updateInputs(self, inputs:PivotIOInputs) -> None:
        pass

    def run(self) -> None:
        pass

    def setPosition(self, degrees:float) -> None:
        pass

    def getPosition(self) -> float:
        return 0.0

    def atSetpoint(self, errorRange:float=0.0) -> bool:
        sp = self.getSetpoint()
        pos = self.getPosition()
        atPos = abs( sp - pos ) < errorRange
        return atPos
    
    def getSetpoint(self) -> float:
        return 0.0

    def syncEncoder(self) -> None:
        pass