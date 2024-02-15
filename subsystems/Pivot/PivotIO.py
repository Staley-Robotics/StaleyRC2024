from wpiutil.wpistruct import make_wpistruct

from dataclasses import dataclass


class PivotIO:
    @make_wpistruct(name="PivotIOInputs")
    @dataclass
    class PivotIOInputs:
        motorTempCelsius:float = 0.0
        motorVoltage:float = 0.0
        motorCurrent:float = 0.0
        motorVelocity:float = 0.0
    
        motorPosition:float = 0.0
        desiredMotorPosition:float = 0.0
    
    def __init__(self) -> None:
        pass
        
    def update_inputs(self, inputs:PivotIOInputs):
        pass