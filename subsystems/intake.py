import commands2
from commands2.command import Command
import phoenix5
from wpilib import *
from rev import *
from phoenix5 import *
import wpilib


# 2 infrared sensors

"""
    if front infrared && back infrared:
        Intake velocity = 0
    elif frontend:
        Intake pulls in
    elif backend:
        Intake pushes forward till 0
"""

# NOTE ON IR SENSORS: The receiver can give false positives negatives due to ambient IR
# (such as sunshine but also other sources). We put a “hood” of electrical tape across 
# the top and down both sides that extended a bit out in front of the receiver (do not block the path from the emitter)

class Intake(commands2.Subsystem):
    """
    Contains functions related to the operation of the intake.
    
    Has Functions:

        getVelocity() -> float

        getTargetVel() -> float

        setTargetVel() -> None

        atTargetVel() -> bool
    """

    targetVel: float

    def __init__(self):
        super().__init__()
        # Motor initialization
        self.uMotor = WPI_TalonSRX(20)
        self.lMotor = WPI_TalonSRX(21)

        # Encoder initialization
        self.uMotor.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative)
        self.lMotor.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative)

        self.uMotor.setNeutralMode(phoenix5.NeutralMode(2))
        self.lMotor.setNeutralMode(phoenix5.NeutralMode(2))
        

        # IR Sensor initialization
        self.frontIR = DigitalInput(0)
        self.backIR = DigitalInput(1)

        # No PID required

        # Other INITS
        self.targetVel = 0.0
        self.RuntimeVel = 0.0

        self.setName( "intake" )


    def periodic(self) -> None:
        # Smart Dashboard information output
        SmartDashboard.putNumber("Upper Motor Applied Output", self.uMotor.getMotorOutputPercent())
        SmartDashboard.putNumber("Lower Motor Applied Output", self.lMotor.getMotorOutputPercent())
        SmartDashboard.putNumber("Upper Motor Voltage", self.uMotor.getMotorOutputVoltage())
        SmartDashboard.putNumber("Lower Motor Voltage", self.lMotor.getMotorOutputVoltage())
        SmartDashboard.putNumber("Upper Motor Velocity", self.uMotor.getSelectedSensorVelocity())
        SmartDashboard.putNumber("Lower Motor Velocity", self.lMotor.getSelectedSensorVelocity())
        SmartDashboard.putNumber("Upper Motor Current", self.uMotor.getStatorCurrent())
        SmartDashboard.putNumber("Lower Motor Current", self.lMotor.getStatorCurrent())
        SmartDashboard.putNumber("Upper Motor Temp", self.uMotor.getTemperature())
        SmartDashboard.putNumber("Lower Motor Temp", self.lMotor.getTemperature())
        SmartDashboard.putNumber("Target Velocity", self.targetVel)
        SmartDashboard.putBoolean("@Velocity", self.atTargetVel())
        
        return super().periodic()


    """
    START IR SENSOR FUNCTIONS   
    """
    def getFrontIR(self) -> bool:
        return self.frontIR.get()

    def getBackIR(self) -> bool:
        return self.backIR.get()


    """
    END IR SENSORS
    """

    def simulationPeriodic(self) -> None:
        return super().simulationPeriodic()
    

    def getVelocity(self) -> tuple[float, float]:
        """
        Returns the velocity of the intake motors in form (upper motor velocity, lower motor velocity)
        """
        return (self.uMotor.getSelectedSensorVelocity(), self.lMotor.getSelectedSensorVelocity())
    

    def getTargetVel(self) -> float:
        return self.targetVel
    

    def setTargetVel(self, velocity) -> None:
        self.targetVel = velocity


    def runMotors(self) -> None:
        self.uMotor.set(ControlMode.PercentOutput, self.targetVel)
        self.lMotor.set(ControlMode.PercentOutput, -self.targetVel)


    def getRuntimeVel(self) -> float:
        return self.RuntimeVel
    
    
    def setRuntimeVel(self, velocity) -> None:
        self.RuntimeVel = velocity
        print(velocity)


    def atTargetVel(self) -> bool:
        return ((abs(self.uMotor.getSelectedSensorVelocity() - self.targetVel) < 0.05) and (abs(self.lMotor.getSelectedSensorVelocity() - self.targetVel) < 0.05))
