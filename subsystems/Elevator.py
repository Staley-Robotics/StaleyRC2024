import wpilib

import wpiutil.wpistruct
import dataclasses
from rev import CANSparkMax, CANSparkLowLevel, SparkPIDController
from wpilib import SmartDashboard
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
        
        
        #Probably have to invert one of these motors to work right
        self.lmotor = CANSparkMax(0, CANSparkLowLevel.MotorType.kBrushless)
        self.rmotor = CANSparkMax(1, CANSparkLowLevel.MotorType.kBrushless)

        self.lpid = self.lmotor.getPIDController()
        self.rpid = self.rmotor.getPIDController()

        self.lencoder = self.lmotor.getEncoder()
        self.rencoder = self.rmotor.getEncoder()

        self.lpid.setFeedbackDevice(self.lencoder)
        self.rpid.setFeedbackDevice(self.rencoder)
        


        #---------------Tunables---------------
        
        self.tuneP  = NTTunableFloat("Elevator/P_Gain",  0.0, persistent=True)
        self.tuneI  = NTTunableFloat("Elevator/I_Gain",  0.0, persistent=True)
        self.tuneD  = NTTunableFloat("Elevator/D_Gain",  0.0, persistent=True)
        self.tuneFF = NTTunableFloat("Elevator/FF_Gain", 0.0, persistent=True)
        self.motor_max_speed = NTTunableFloat('Elevator/motor_max_speed', 1.0, persistent=False)
        self.motor_min_speed = NTTunableFloat("Elevator/motor_min_speed", -1.0, persistent=False)
        self.increment = NTTunableFloat("Elevator/incrementVal", 0.05, persistent=False)


        #--------------PID values--------------
        self.kP =  0
        self.kI =  0
        self.kD =  0
        self.kFF = 0

        self.kMaxOutput =  1
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
        self.rpid.setReference(target, CANSparkMax.ControlType.kPosition)
        self.lpid.setReference(target, CANSparkMax.ControlType.kPosition)
        
    
    #---------------Main functions-------------

    def getPosition(self):
        return self.rencoder.getPosition()

    def atPosition(self, target:float):
        return target-0.1 < self.getPosition() < target+0.1
    #                                               _
    def getSetpoint(self) -> float: #                |
        return self.setPoint #                       |
    #                                                |-- Likely to remove these, they seem futile
    def setSetpoint(self, target:float) -> None: #   |
        self.setPoint=target #                      _|

    
    #------------TESTING FUNCTIONS-------------

    def invertInc(self) -> None:
        self.invertVal *= -1

    def incrementP(self, val=None) -> None:
        if not val: val = self.increment.get() * self.invertVal
        self.kP += val
        self.tuneP.set(self.kP)
        self.setP(self.kP)

    def incrementI(self, val=None) -> None:
        if not val: val = self.increment.get() * self.invertVal
        self.kI += val
        self.tuneI.set(self.kI)
        self.setI(self.kI)

    def incrementD(self, val=None) -> None:
        if not val: val = self.increment.get() * self.invertVal
        self.kD += val
        self.tuneD.set(self.kD)
        self.setD(self.kD)

    def incrementFF(self, val=None) -> None:
        if not val: val = self.increment.get() * self.invertVal
        self.kFF += val
        self.tuneFF.set(self.kFF)
        self.setFF(self.kFF)


    #------------Periodic Functions------------

    def periodic(self) -> None:
        """
        do any necessary updates
        """
        self.setReference(self.getSetpoint())
        SmartDashboard.putNumberArray("Encoder position", [self.rencoder.getPosition(), self.lencoder.getPosition()])
        return super().periodic()

    def simulationPeriodic(self) -> None:
        return super().simulationPeriodic()
