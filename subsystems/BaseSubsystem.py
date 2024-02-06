import wpilib

import wpiutil.wpistruct
import dataclasses

import commands2

from util import *

class BaseSubsystem(commands2.Subsystem):
    """
    Subsystem to handle things
    """

    @wpiutil.wpistruct.make_wpistruct(name='launcherinputs')
    @dataclasses.dataclass
    class SubsystemInputs:
        '''
        A WPIStruct object containing all Subsystem data
        This is meant to simplify logging of contained data
        '''
        #put logging data here

    def __init__(self):
        super().__init__()

        #---------------Tunables---------------

        #-------------Whatever you want------------

    def periodic(self) -> None:
        """
        do any necessary updates
        """
        return super().periodic()
    
    def simulationPeriodic(self) -> None:
        return super().simulationPeriodic()
