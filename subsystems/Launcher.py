import wpilib

import phoenix5
import rev

import commands2

from util import *

class Launcher(commands2.Subsystem):
    """
    Subsystem to handle double flywheel note launcher
    """
    def __init__(self):
        super().__init__()

        #---------------CONSTANTS ISH---------------
        self.defaultIncrement = NTTunableFloat('Launcher/defaultIncrement', 0.05, persistent=True)
        self.lFlywheelPort = NTTunableInt('Launcher/lFlywheelPort', 14, persistent=True)
        self.rFlywheelPort = NTTunableInt('Launcher/rFlywheelPort', 18, persistent=True)

        self.lFlywheelInverted = NTTunableBoolean('Launcher/lFlywheelInverted', True, persistent=False, updater=lambda : self.l_launcher_motor.setInverted(self.lFlywheelInverted.get()))
        self.rFlywheelInverted = NTTunableBoolean('Launcher/rFlywheelInverted', False, persistent=False, updater=lambda : self.r_launcher_motor.setInverted(self.rFlywheelInverted.get()))

        self.defaultSpeed = NTTunableFloat('Launcher/defaultSpeed', 0.8, persistent=True)
        self.maxSpeed = NTTunableFloat('Launcher/maxSpeed', 0.95, persistent=True)
        self.minSpeed = NTTunableFloat('Launcher/minSpeed', 0.1, persistent=True)

        #-------------MOTORS-------------
        #self.l_launcher_motor = phoenix5.WPI_TalonSRX(self.lFlywheelPort.get())
        self.l_launcher_motor = rev.CANSparkMax(self.lFlywheelPort.get(), rev.CANSparkMax.MotorType.kBrushless)
        self.l_launcher_motor.setInverted(self.lFlywheelInverted.get())
        #self.r_launcher_motor = phoenix5.WPI_TalonSRX(self.rFlywheelPort.get())
        self.r_launcher_motor = rev.CANSparkMax(self.rFlywheelPort.get(), rev.CANSparkMax.MotorType.kBrushless)
        self.r_launcher_motor.setInverted(self.rFlywheelInverted.get())
        #self.shooterMotors = wpilib.MotorControllerGroup(self.l_launcher_motor, self.r_launcher_motor)

        #-------------SPEED HANDLING------------
        self.is_running = NTTunableBoolean('Launcher/is_running', False)
        #stored speed motors will run when activated
        self.speed = NTTunableFloat('Launcher/stored_speed', self.defaultSpeed.get())
        #actual motor speed setting
        self.actual_speed = NTTunableFloat('Launcher/actual_set_speed',0.0)

        

    def periodic(self) -> None:
        self.l_launcher_motor.set(self.actual_speed.get())
        self.r_launcher_motor.set(self.actual_speed.get())
    
    def simulationPeriodic(self) -> None:
        return super().simulationPeriodic()
    
    def start_launcher(self):
        """changes launcher speed to current stored speed"""
        self.is_running.set(True)
        self.actual_speed.set(self.speed.get())
    
    def stop_launcher(self):
        '''changes launcher speed to 0.0'''
        self.is_running.set(False)
        self.actual_speed.set(0.0)
    
    def increment_speed(self, amnt=None):
        """
        increase stored motor speed by input amount or default value
        automatically updates actual speed if launcher is running
        """
        if amnt is None: amnt = self.defaultIncrement.get()
        self.speed.set(min(self.speed.get() + amnt, self.maxSpeed.get()))
        if self.is_running.get(): self.actual_speed.set(self.speed.get())
    def decrement_speed(self, amnt=None):
        """
        decrease stored motor speed by input amount or default value
        automatically updates actual speed if launcher is running
        """
        if amnt is None: amnt = self.defaultIncrement.get()
        self.speed.set(max(self.speed.get() - amnt, self.minSpeed.get()))

        if self.is_running.get(): self.actual_speed.set(self.speed.get())
