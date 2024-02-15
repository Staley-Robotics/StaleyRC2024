import wpilib

import wpiutil.wpistruct
import dataclasses

from commands2 import Subsystem

from phoenix5 import *
from phoenix5.sensors import CANCoder

from util import *

class Pivot(Subsystem):
    """
    Parent Subsystem to handle a one-motor pivot, which the Launcher/Indexer is attached to
    
    mostly just for logging setup
    """

    @wpiutil.wpistruct.make_wpistruct(name='ShooterPivotInputs')
    @dataclasses.dataclass
    class PivotInputs:
        """
        A WPIStruct object containing all Subsystem data
        This is meant to simplify logging of contained data
        """
        motorTempCelsius:float = 0.0
        motorVoltage:float = 0.0
        motorCurrent:float = 0.0
        motorVelocity:float = 0.0

        motorPosition:float = 0.0
        desiredMotorPosition:float = 0.0

    def __init__(self):
        super().__init__()

        self.pivotSpeedMult = NTTunableFloat('Pivot/Speed Multiplier', 0.1, persistent=True)
        self.actualSpeed = NTTunableFloat('Pivot/Actual Speed', 0.0)

    def periodic(self) -> None:
        """
        do any necessary updates
        """
        pass
