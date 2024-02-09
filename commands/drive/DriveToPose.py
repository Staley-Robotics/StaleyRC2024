# Import Python
import math

# Import FRC
from commands2 import Command
from wpilib import Timer
from wpimath.kinematics import SwerveDrive4Kinematics, SwerveModuleState
from wpimath.controller import PIDController, ProfiledPIDControllerRadians, HolonomicDriveController
from wpimath.geometry import Translation2d
from wpimath.trajectory import Trajectory, TrajectoryConfig, TrajectoryGenerator, TrapezoidProfileRadians
#from pathplannerlib import PathConstraints, PathPlanner, PathPlannerTrajectory, PathPoint

# Import Subsystems and Commands
from subsystems import *

class DriveToPose(Command):
    _m_controller: HolonomicDriveController = None
    swerveDrive: SwerveDrive = None
    
    def __init__(self, swerveDrive:SwerveDrive, getTargetPose:typing.Callable[[], Pose2d]):
        super().__init__()
        self.swerveDrive = swerveDrive
        self.getTargetPose = getTargetPose
        self.addRequirements( swerveDrive )
        self.setName( "DriveToPose" )

    def initialize(self):
        self.swerveDrive.resetHolonomicDriveController()
        self._m_controller = self.swerveDrive.getHolonomicDriveController()


    def execute(self):
        currentPose = self.swerveDrive.getPose()
        targetPose = self.getTargetPose()

        cSpeeds = self._m_controller.calculate( currentPose, targetPose, 0, targetPose.rotation() )
        self.swerveDrive.runChassisSpeeds( cSpeeds, False )

    def end(self, interrupted:bool) -> None:
        #self.swerveDrive.stop()
        pass

    def isFinished(self) -> bool:
        return self._m_controller.atReference()