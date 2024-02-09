import commands2
from commands2.command import Command

import wpilib

import wpiutil
import dataclasses

import rev
import phoenix5

from util import *

class Intake(commands2.Subsystem):
    """
    Contains functions related to the operation of the intake.
    
    Has Functions:

        getVelocity() -> float

        getTargetVel() -> float

        setTargetVel() -> None

        atTargetVel() -> bool
    """
    @wpiutil.wpistruct.make_wpistruct(name='IntakeInputs')
    @dataclasses.dataclass
    class IntakeInputs:
        '''
        A WPIStruct object containing all Subsystem data
        This is meant to simplify logging of contained data
        '''
        #put logging data here

        uMotorAppliedOutput: float
        uMotorVoltage: float
        uMotorVelocity: float
        uMotorCurrent: float
        uMotorTempCelsius: float

        lMotorAppliedOutput: float
        lMotorVoltage: float
        lMotorVelocity: float
        lMotorCurrent: float
        lMotorTempCelsius: float

        targetVelocity: float
        atVelocity: bool

    def __init__(self):
        super().__init__()
        #tunabels
        self.uMotorInverted = NTTunableBoolean('Intake/Upper Motor Inverted', False, updater=lambda:self.uMotor.setInverted(self.uMotorInverted.get()))
        self.lMotorInverted = NTTunableBoolean('Intake/Lower Motor Inverted', False, updater=lambda:self.lMotor.setInverted(self.lMotorInverted.get()))


        # Motor initialization
        self.uMotor = phoenix5.WPI_TalonFX(3)
        self.lMotor = phoenix5.WPI_TalonFX(4)

        # # Encoder initialization
        #self.uEncoder = self.uMotor.getEncoder()
        #self.lEncoder = self.lMotor.getEncoder()
        
        # No PID required

        # Other INITS
        self.runVel = NTTunableFloat('Intake/run velocity', 0.0, persistent=False)
        self.targetVel = 0.0
        self.RuntimeVel = 0.0


    def periodic(self) -> None:
        # Smart Dashboard information output
        self.runMotors()
        return super().periodic()

    def updateInputs(self, inputs: IntakeInputs):
        inputs.uMotorAppliedOutput: float = self.uMotor.getAppliedOutput()
        inputs.uMotorVoltage: float = self.uMotor.getBusVoltage()
        inputs.uMotorVelocity: float = self.uEncoder.getVelocity()
        inputs.uMotorCurrent: float =  self.uMotor.getOutputCurrent()
        inputs.uMotorTempCelsius: float =  self.uMotor.getMotorTemperature()

        inputs.lMotorAppliedOutput: float = self.uMotor.getAppliedOutput()
        inputs.lMotorVoltage: float = self.uMotor.getBusVoltage()
        inputs.lMotorVelocity: float = self.uEncoder.getVelocity()
        inputs.lMotorCurrent: float = self.uMotor.getOutputCurrent()
        inputs.lMotorTempCelsius: float = self.uMotor.getMotorTemperature()

        inputs.targetVelocity: float = self.targetVel
        inputs.atVelocity: bool = self.atTargetVel()

    
    def simulationPeriodic(self) -> None:
        return super().simulationPeriodic()
    

    def getVelocity(self) -> tuple[float, float]:
        """
        Returns the velocity of the intake motors in form (upper motor velocity, lower motor velocity)
        """
        return (self.uEncoder.getVelocity(), self.lEncoder.getVelocity())
    

    def getTargetVel(self) -> float:
        return self.targetVel
    

    def setTargetVel(self, velocity) -> None:
        self.targetVel = velocity

    def runMotors(self) -> None:
        self.uMotor.set(self.runVel.get())
        self.lMotor.set(self.runVel.get())

    def run(self, reversed=False):
        self.setTargetVel(self.runVel.get() * (-1 if reversed else 1))
    def stop(self):
        self.setTargetVel(0)

    def getRuntimeVel(self) -> float:
        return self.RuntimeVel
    
    def setRuntimeVel(self, velocity) -> None:
        self.RuntimeVel = velocity
        print(velocity)

    def atTargetVel(self) -> bool:
        return ((abs(self.uEncoder.getVelocity() - self.targetVel) < 0.05) and (abs(self.lEncoder.getVelocity() - self.targetVel) < 0.05))