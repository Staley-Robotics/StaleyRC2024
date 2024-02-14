import dataclasses

import wpiutil.wpistruct

class LauncherIO:

    @wpiutil.wpistruct.make_wpistruct(name="LauncherIOInputs")
    @dataclasses.dataclass
    class LauncherIOInputs:
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

        sensor: bool = False

    def __init__(self):
        pass

    def updateInputs(self, inputs:LauncherIOInputs) -> None:
        pass

    def run(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def setVelocity(self, leftVelocity:float, rightVelocity:float) -> None:
        pass

    def getVelocity(self) -> [float, float]:
        pass

    def atSetpoint(self) -> [bool, bool]:
        pass
    
    def getSetpoint(self) -> [float, float]:
        pass

