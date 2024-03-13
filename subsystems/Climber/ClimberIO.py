import dataclasses

import wpiutil.wpistruct

class ClimberIO:

    @wpiutil.wpistruct.make_wpistruct(name="ClimberIOInputs")
    @dataclasses.dataclass
    class ClimberIOInputs:
        #Left Motor
        leftAppliedVolts: float = 0.0
        leftCurrentAmps: float = 0.0
        leftTempCelcius: float = 0.0
        leftVelocity: float = 0.0
        leftPosition: float = 0.0

        #Right Motor
        rightAppliedVolts: float = 0.0
        rightCurrentAmps: float = 0.0
        rightTempCelcius: float = 0.0
        rightPosition: float = 0.0
        rightVelocity: float = 0.0

    def __init__(self):
        pass

    def updateInputs(self, inputs:ClimberIOInputs) -> None:
        pass

    def run(self) -> None:
        pass

    def setBrake(self, brake:bool) -> None:
        pass

    def setPosition(self, leftPosition:float, rightPosition:float) -> None:
        pass

    def movePosition(self, leftRate:float, rightRate:float) -> None:
        pass

    def resetPosition(self, position:float) -> None:
        pass

    def getPosition(self) -> [float, float]:
        return [ 0.0, 0.0 ]

    def atSetpoint(self, errorRange:float = 100.0) -> [bool,bool]:
        leftPos, rightPos = self.getPosition()
        leftSp, rightSp = self.getSetpoint()
        leftAtPos = abs( leftSp - leftPos ) < errorRange
        rightAtPos = abs( rightSp - rightPos ) < errorRange
        return [ leftAtPos, rightAtPos ]
    
    def getSetpoint(self) -> [float,float]:
        return [ 0.0, 0.0 ]
    
