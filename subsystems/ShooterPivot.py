import wpilib

import wpiutil.wpistruct
import dataclasses

import commands2

import rev

from util import *

class ShooterPivot(commands2.Subsystem):
    """
    Subsystem to handle a one-motor pivot, which the Launcher is attached to
    """

    @wpiutil.wpistruct.make_wpistruct(name='launcherinputs')
    @dataclasses.dataclass
    class ShooterPivotInputs:
        '''
        A WPIStruct object containing all Subsystem data
        This is meant to simplify logging of contained data
        '''
        #put logging data here

    def __init__(self):
        super().__init__()

        #---------------Tunables---------------


        #-------------Motors------------
        self.motor = rev.CANSparkMax(4, rev.CANSparkMax.MotorType.kBrushless)

    def periodic(self) -> None:
        """
        do any necessary updates
        """
        return super().periodic()

    def go_to(self):
        '''
        not a clue
        '''
    
    def simulationPeriodic(self) -> None:
        return super().simulationPeriodic()
