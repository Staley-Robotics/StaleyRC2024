import dataclasses

import wpiutil.wpistruct

class ClimberIO:

    @wpiutil.wpistruct.make_wpistruct(name="ClimberIOInputs")
    @dataclasses.dataclass
    class ClimberIOInputs:
        #Left Motor
        lMotorAppliedVolts: float = 0.0
        lMotorCurrentAmps: float = 0.0
        lMotorTempCelcius: float = 0.0

        lMotorPosition: float = 0.0
        lMotorDesiredPosition: float = 0.0

        #Right Motor
        rMotorAppliedVolts: float = 0.0
        rMotorCurrentAmps: float = 0.0
        rMotorTempCelcius: float = 0.0

        rMotorPosition: float = 0.0
        rMotorDesiredPosition: float = 0.0

    def __init__(self):
        pass

    def updateInputs(self, inputs:ClimberIOInputs) -> None:
        pass

    def updateLeft(self) -> None: pass
    def updateRight(self): pass
    
    def setBrake(self, brake:bool) -> None: pass
    
    def getLPosition(self): pass
    def getLPosition(self): pass

    def setLPosition(self, position:int): pass
    def setRPosition(self, position:int): pass
