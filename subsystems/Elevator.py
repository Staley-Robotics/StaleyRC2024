import wpilib

import wpiutil.wpistruct
import dataclasses
from rev import CANSparkMax, CANSparkLowLevel, SparkPIDController

import commands2

from util import *

class Elevator(commands2.Subsystem):
    """
    Subsystem to handle a 2 motor elevator
    """
    
    @wpiutil.wpistruct.make_wpistruct(name="Elevator")
    @dataclasses.dataclass
    class ElevatorInputs:
        motorVoltage:float = 0
        motorPosition:float = 0
        
    def __init__(self):
        super().__init__()

        #----------------------PID & MOTORS----------------------
        self.setPoint:float=0
        self.invertVal:int=1
        

        self.lmotor = CANSparkMax(0, CANSparkLowLevel.MotorType.kBrushless)
        self.rmotor = CANSparkMax(1, CANSparkLowLevel.MotorType.kBrushless)

        self.lpid = self.lmotor.getPIDController()
        self.rpid = self.rmotor.getPIDController()

        self.lencoder = self.lmotor.getEncoder()
        self.rencoder = self.rmotor.getEncoder()

        self.lpid.setFeedbackDevice(self.lencoder)
        self.rpid.setFeedbackDevice(self.rencoder)
        


        #---------------Tunables---------------
        
        self.tuneP  = NTTunableFloat("Elevator/P_Gain",  0.0)
        self.tuneI  = NTTunableFloat("Elevator/I_Gain",  0.0)
        self.tuneD  = NTTunableFloat("Elevator/D_Gain",  0.0)
        self.tuneFF = NTTunableFloat("Elevator/FF_Gain", 0.0)
        self.motor_set_speed = NTTunableFloat('Elevator/motor_set_speed', 0.0)
        self.motor_actual_speed = NTTunableFloat('Elevator/MotorSpeed', 0.0)

        #--------------PID values--------------
        self.kP = 0 
        self.kI = 0
        self.kD = 0
        self.kFF = 0

        self.kMaxOutput = 1
        self.kMinOutput = -1

        # Set PID coefficients
        self.setP(self.kP)
        self.setI(self.kI)
        self.setD(self.kD)
        self.setFF(self.kFF)
        self.setOutputRange(self.kMinOutput, self.kMaxOutput)

    #----------Simplifying changing PID---------

    def setP(self, val:float) -> None:
        self.rpid.setP(val)
        self.lpid.setP(val)

    def setI(self, val:float) -> None:
        self.rpid.setI(val)
        self.lpid.setI(val)

    def setD(self, val:float) -> None:
        self.rpid.setI(val)
        self.lpid.setD(val)

    def setFF(self, val:float) -> None:
        self.rpid.setFF(val)
        self.lpid.setFF(val)

    def setOutputRange(self, min:float, max:float) -> None:
        self.rpid.setOutputRange(min, max)
        self.lpid.setOutputRange(min, max)

    def setReference(self, target:float) -> None:
        """
        For target, use self.getSetpoint() or self.setPoint
        """
        self.rpid.setReference(target * self.invertVal, CANSparkMax.ControlType.kPosition)
        self.lpid.setReference(target * self.invertVal, CANSparkMax.ControlType.kPosition)
        
    
    #---------------Main functions-------------


    def getPosition(self):
        return self.rencoder.getPosition()

    def atPosition(self, target:float):
        return target-0.1 < target < target+0.1
    #                                               _
    def getSetpoint(self) -> float: #                |
        return self.setPoint #                       |
    #                                                |-- Likely to remove these, they seem futile
    def setSetpoint(self, target:float) -> None: #   |
        self.setPoint=target #                      _|

    def invertRef(self) -> None:
        self.invertVal *= -1

    

    def periodic(self) -> None:
        """
        do any necessary updates
        """
        self.setReference(self.getSetpoint())

        return super().periodic()

    def simulationPeriodic(self) -> None:
        return super().simulationPeriodic()
