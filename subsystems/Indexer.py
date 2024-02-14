import wpilib

import wpiutil.wpistruct
import dataclasses

import commands2

import phoenix5

from util import *

class Indexer(commands2.Subsystem):
    """
    Subsystem to handle a one-motor indexer, supplies notes to launcher, recieves from intake
    """

    @wpiutil.wpistruct.make_wpistruct(name='launcherinputs')
    @dataclasses.dataclass
    class IndexerInputs:
        '''
        A WPIStruct object containing all Indexer data
        This is meant to simplify logging of contained data
        '''
        #motor inputs
        motorAppliedVolts:float = 0
        motorCurrentAmps:float = 0
        motorTempCelsius:float = 0

    def __init__(self):
        super().__init__()

        #---------------Tunables---------------
        self.motor_set_speed = NTTunableFloat('Indexer/motor_set_speed', 0.0)
        self.motor_actual_speed = NTTunableFloat('Indexer/motor_actual_speed', 0.0)
        self.motor_inverted = NTTunableBoolean('Indexer/direction_inverted', False, updater=lambda: self.motor.setInverted(self.motor_inverted.get()))

        #-------------Motors------------
        self.motor = phoenix5.WPI_TalonFX(16)

    def periodic(self) -> None:
        """
        do any necessary updates
        """
        self.motor.set(self.motor_actual_speed.get())
    
    def run(self):
        '''
        start indexer motor spinning at 'motor_set_speed' until stop() is called
        '''
        self.motor_actual_speed.set(self.motor_set_speed.get())
    def stop(self):
        '''
        set indexer motor speed to 0
        '''
        self.motor_actual_speed.set(0)
    
    def simulationPeriodic(self) -> None:
        return super().simulationPeriodic()
