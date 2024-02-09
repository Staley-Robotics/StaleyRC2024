import wpilib

import wpiutil.wpistruct
import dataclasses

import commands2

from util import *

'''
NOTE:
two motors is weird, same voltage=dif speed, how??? 
PID and crossing feedback device proabl idk
'''


class Elevator(commands2.Subsystem):
    """
    Subsystem to handle a 2(probalby) motor elevator
    """

    @wpiutil.wpistruct.make_wpistruct(name='elevatorinputs')
    @dataclasses.dataclass
    class ElevatorInputs:
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
