import wpilib
import wpimath

import commands2

from constants import LauncherConsts as LCs

class Launcher(commands2.Subsystem):
    """
    Subsystem to handle double flywheel note launcher
    """
    def __init__(self):
        super().__init__()
        #TODO: find actual motor type to be used
        self.l_launcher_motor = wpilib.Talon(LCs.lFlywheelPort) #NOTE: arbitrary channel chosen
        self.l_launcher_motor.setInverted(LCs.lFlywheelInverted) #NOTE: assuming r motor turns clockwise by default
        self.r_launcher_motor = wpilib.Talon(LCs.rFlywheelPort)
        self.r_launcher_motor.setInverted(LCs.rFlywheelInverted)

        #self.shooterMotors = wpilib.MotorControllerGroup(self.l_launcher_motor, self.r_launcher_motor)

    def periodic(self) -> None:
        return super().periodic()
    
    def simulationPeriodic(self) -> None:
        return super().simulationPeriodic()
    
    def start_launcher(self):
        """
        INCOMPLETE
        currently, sets motor speed to 0.8

        could vary speed based on calculated distance,
        or just launch it really fast every time, idk
        """
        self.l_launcher_motor.set(0.8)
        self.r_launcher_motor.set(0.8)
    
    def stop_launcher(self):
        self.l_launcher_motor.stopMotor()
        self.r_launcher_motor.stopMotor()