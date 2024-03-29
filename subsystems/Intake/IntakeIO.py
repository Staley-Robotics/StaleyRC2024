import dataclasses

import wpiutil.wpistruct

class IntakeIO:

    @wpiutil.wpistruct.make_wpistruct(name="IntakeIOInputs")
    @dataclasses.dataclass
    class IntakeIOInputs:
        lowerPosition: float = 0
        lowerVelocity: float = 0
        lowerAppliedVolts: float = 0
        lowerCurrentAmps: float = 0
        lowerTempCelcius: float = 0

        upperPosition: float = 0
        upperVelocity: float = 0
        upperAppliedVolts: float = 0
        upperCurrentAmps: float = 0
        upperTempCelcius: float = 0

        sensor: bool = False

    def __init__(self):
        pass

    def updateInputs(self, inputs:IntakeIOInputs) -> None:
        pass

    def run(self) -> None:
        pass

    def setBrake(self, brake:bool) -> None:
        pass

    def setVelocity(self, upperVelocity:float, lowerVelocity:float) -> None:
        pass

    def getVelocity(self) -> [float, float]:
        return [ 0.0, 0.0 ]

    def atSetpoint(self, errorRange:float = 0.0) -> [bool,bool]:
        upperVeloc, lowerVeloc = self.getVelocity()
        upperSp, lowerSp = self.getSetpoint()
        upperAtSpeed = abs( upperSp - upperVeloc ) < errorRange
        lowerAtSpeed = abs( lowerSp - lowerVeloc ) < errorRange
        return [ upperAtSpeed, lowerAtSpeed ]
    
    def getSetpoint(self) -> float:
        return [ 0.0, 0.0 ]
    
    def getSensorIsBroken(self) -> float:
        return False
    
    def foundNote(self) -> float:
        return False
