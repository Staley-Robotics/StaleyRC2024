import wpilib

import rev
import phoenix5

from util import *
from subsystems import Launcher
from ntcore import *

from util import *

class LauncherSparkMaxWFeed(Launcher):
    """
    Subsystem to handle double flywheel note launcher
    """
    def __init__(self):
        super().__init__()

        self.lFlywheelInverted = NTTunableBoolean('Launcher/lFlywheelInverted', True, persistent=False, updater=lambda : self.lMotor.setInverted(self.lFlywheelInverted.get()))
        self.rFlywheelInverted = NTTunableBoolean('Launcher/rFlywheelInverted', False, persistent=False, updater=lambda : self.rMotor.setInverted(self.rFlywheelInverted.get()))


        #-------------MOTORS-------------
        self.lMotor = rev.CANSparkMax(9, rev.CANSparkMax.MotorType.kBrushless)
        self.lMotor.setInverted(self.lFlywheelInverted.get())
        self.rMotor = rev.CANSparkMax(8, rev.CANSparkMax.MotorType.kBrushless)
        self.rMotor.setInverted(self.rFlywheelInverted.get())

        self.feederMotor = rev.CANSparkMax(20, rev.CANSparkMax.MotorType.kBrushless)
        self.feeder_speed = NTTunableFloat('Launcher/Feeder_speed', 0.5)
        self.feeder_actual = NTTunableFloat('Launcher/Active_speed', 0)
        
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

        #feeder
        self.feederMotor.set(self.feeder_actual.get())
    
    def updateInputs(self, inputs: Launcher.LauncherInputs):
        inputs.lMotorAppliedVolts = self.lMotor.getAppliedOutput() * self.lMotor.getBusVoltage()
        inputs.lMotorurrentAmps = self.lMotor.getOutputCurrent()
        inputs.lMotorTempCelcius = self.lMotor.getMotorTemperature()

        inputs.rMotorAppliedVolts = self.rMotor.getAppliedOutput() * self.rMotor.getBusVoltage()
        inputs.rMotorurrentAmps = self.rMotor.getOutputCurrent()
        inputs.rMotorTempCelcius = self.rMotor.getMotorTemperature()
    
    def run_feeder(self, reversed=False):
        self.feeder_actual.set(self.feeder_speed.get() * (-1 if reversed else 1))
    def stop_feeder(self):
        self.feeder_actual.set(0)
    
    def simulationPeriodic(self) -> None:
        return super().simulationPeriodic()
