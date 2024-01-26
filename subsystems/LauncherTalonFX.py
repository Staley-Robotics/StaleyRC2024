import wpilib

import phoenix5
import rev

import commands2

from util import *
from subsystems import Launcher

class LauncherTalonFX(Launcher):
    """
    Subsystem to handle double flywheel note launcher
    """
    def __init__(self):
        super().__init__()

        #-------------MOTORS-------------
        self.l_launcher_motor = phoenix5.WPI_TalonFX(3)
        self.l_launcher_motor.setInverted(self.lFlywheelInverted.get())
        self.r_launcher_motor = phoenix5.WPI_TalonFX(4)
        self.r_launcher_motor.setInverted(self.rFlywheelInverted.get())

    def periodic(self) -> None:
        #logging

        #run motors
        self.l_launcher_motor.set(self.actual_speed.get())
        self.r_launcher_motor.set(self.actual_speed.get())
    
    def simulationPeriodic(self) -> None:
        return super().simulationPeriodic()
