import wpilib

import wpiutil.wpistruct
import dataclasses

import commands2

import rev
import phoenix5

from util import *

class ShooterPivot(commands2.Subsystem):
    """
    Subsystem to handle a one-motor pivot, which the Launcher is attached to
    """

    @wpiutil.wpistruct.make_wpistruct(name='ShooterPivotInputs')
    @dataclasses.dataclass
    class ShooterPivotInputs:
        '''
        A WPIStruct object containing all Subsystem data
        This is meant to simplify logging of contained data
        '''
        #put logging data here
        thing:float = 0

    def __init__(self):
        super().__init__()

        #---------------Tunables---------------
        self.pivotKP = NTTunableFloat('Pivot/PID_kP', 0.2, updater=lambda:..., persistent=True)
        self.pivotKI = NTTunableFloat('Pivot/PID_kI', 0.0, updater=lambda:..., persistent=True)
        self.pivotKD = NTTunableFloat('Pivot/PID_kD', 0.0, updater=lambda:..., persistent=True)
        self.pivotKFF = NTTunableFloat('Pivot/PID_kFF', 0.2, updater=lambda:..., persistent=True)

        self.pivotSpeedMult = NTTunableFloat('Pivot/Speed Multiplier', 0.01)
        self.actualSpeed = NTTunableFloat('Pivot/Actual Speed', 0.0)


        #-------------Motors and Stuffs------------
        self.motor = phoenix5.WPI_TalonFX(15)

        self.motorPID = self.motor.getPIDController()
        self.motorPID.setP(self.pivotKP.get())
        self.motorPID.setI(self.pivotKI.get())
        self.motorPID.setD(self.pivotKD.get())
        self.motorPID.setFF(self.pivotKFF.get())

    def periodic(self) -> None:
        """
        do any necessary updates
        """
        self.motor.set(self.actualSpeed.set())

    def go_to(self, angle:float=0):
        '''
        pivot towards angle
        '''
        turnMode = rev.CANSparkMax.ControlType.kPosition
        self.motorPID.setReference(angle, turnMode)
    
   #def set_speed(self, speed):
        
    
    def simulationPeriodic(self) -> None:
        return super().simulationPeriodic()
