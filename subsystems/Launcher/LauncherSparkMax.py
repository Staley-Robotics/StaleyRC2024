import wpilib

import rev

from util import *
from subsystems import Launcher
from ntcore import *

class LauncherSparkMax(Launcher):
    """
    Subsystem to handle double flywheel note launcher
    """
    def __init__(self):
        super().__init__()

        #-------------MOTORS-------------
        self.lMotor = rev.CANSparkMax(20, rev.CANSparkMax.MotorType.kBrushless)
        self.lMotor.setInverted(self.lFlywheelInverted.get())
        self.rMotor = rev.CANSparkMax(9, rev.CANSparkMax.MotorType.kBrushless)
        self.rMotor.setInverted(self.rFlywheelInverted.get())
        
        #logging stuff idk
        self.motorInputs = self.LauncherInputs()
        self.ntMotorInputs = NetworkTableInstance.getDefault().getStructTopic('Launcher/Motors', self.LauncherInputs).publish()

    def periodic(self) -> None:
        #logging
        self.updateInputs(self.motorInputs)
        self.ntMotorInputs.set(self.motorInputs)

        #run motors
        self.lMotor.set(self.actual_speed.get())
        self.rMotor.set(self.actual_speed.get())
    
    def updateInputs(self, inputs: Launcher.LauncherInputs):
        inputs.lMotorAppliedVolts = self.lMotor.getAppliedOutput() * self.lMotor.getBusVoltage()
        inputs.lMotorurrentAmps = self.lMotor.getOutputCurrent()
        inputs.lMotorTempCelcius = self.lMotor.getMotorTemperature()

        inputs.rMotorAppliedVolts = self.rMotor.getAppliedOutput() * self.rMotor.getBusVoltage()
        inputs.rMotorurrentAmps = self.rMotor.getOutputCurrent()
        inputs.rMotorTempCelcius = self.rMotor.getMotorTemperature()
    
    def simulationPeriodic(self) -> None:
        return super().simulationPeriodic()
