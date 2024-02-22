# Import Python
import typing
import math

# Import FRC
from commands2 import Command
from wpilib import Timer
from wpimath.kinematics import SwerveDrive4Kinematics, SwerveModuleState
from wpimath.controller import PIDController, ProfiledPIDControllerRadians, HolonomicDriveController
from wpimath.geometry import Translation2d, Pose2d, Rotation2d
from wpimath.trajectory import Trajectory, TrajectoryConfig, TrajectoryGenerator, TrapezoidProfileRadians
#from pathplannerlib import PathConstraints, PathPlanner, PathPlannerTrajectory, PathPoint

# Import Subsystems and Commands
from subsystems import SwerveDrive

class DriveDistance(Command):
    _m_controller: HolonomicDriveController = None
    swerveDrive: SwerveDrive = None
    
    def __init__(self, swerveDrive:SwerveDrive, distance:typing.Callable[[], Pose2d], heading:typing.Callable[[], Rotation2d] = lambda: None):
        super().__init__()
        self.swerveDrive = swerveDrive
        self.getDistance = distance
        self.getHeading = heading
        self.addRequirements( swerveDrive )
        self.setName( "DriveDistance" )
        self.targetPose = Pose2d(0,0, Rotation2d(0))

    def initialize(self):
        self.swerveDrive.resetHolonomicDriveController()
        self._m_controller = self.swerveDrive.getHolonomicDriveController()
        
        pose = self.swerveDrive.getPose()
        distancePose = self.getDistance()
        newX = pose.X() + distancePose.X()
        newY = pose.Y() + distancePose.Y()
        newR = pose.rotation().rotateBy( distancePose.rotation() )
        if self.getHeading() != None:
            newR = self.getHeading()
        self.targetPose = Pose2d( Translation2d(newX, newY), newR)

    def execute(self):
        currentPose = self.swerveDrive.getPose()
        targetPose = self.targetPose

        cSpeeds = self._m_controller.calculate( currentPose, targetPose, 0, targetPose.rotation() )
        self.swerveDrive.runChassisSpeeds( cSpeeds, False )

    def end(self, interrupted:bool) -> None:
        self.swerveDrive.stop()
        pass

    def isFinished(self) -> bool:
        return self._m_controller.atReference()
