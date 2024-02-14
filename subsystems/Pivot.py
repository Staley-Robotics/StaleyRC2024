import wpilib

from wpiutil.wpistruct import make_wpistruct
from dataclasses import dataclass

from commands2 import Subsystem

from phoenix5 import *
from phoenix5.sensors import CANCoder

from util import *

class Pivot(Subsystem):
    """
    Subsystem to handle a one-motor pivot, which the Launcher/Indexer is attached to
    """

    @make_wpistruct(name='ShooterPivotInputs')
    @dataclass
    class PivotInputs:
        """
        A WPIStruct object containing all Subsystem data
        This is meant to simplify logging of contained data
        """
        motorTempCelsius:float = 0.0

    def __init__(self):
        super().__init__()

        self.pivotSpeedMult = NTTunableFloat('Pivot/Speed Multiplier', 0.01, persistent=True)
        self.actualSpeed = NTTunableFloat('Pivot/Actual Speed', 0.0)

    def periodic(self) -> None:
        """
        do any necessary updates
        """
        pass
