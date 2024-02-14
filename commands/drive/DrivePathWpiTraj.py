# Import Python
import math
import typing

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
from util import Swerve4ControllerCommand

class DrivePathWpiTraj(Swerve4ControllerCommand):
    def __init__(self, swerveDrive:SwerveDrive, getWaypoints:typing.Callable[[], typing.List[Pose2d]], getDesiredHeading:typing.Callable[[], Rotation2d]):
        super().__init__(
            trajectory = Trajectory(),
            pose = swerveDrive.getPose,
            kinematics = swerveDrive.getKinematics(),
            controller = swerveDrive.getHolonomicDriveController(),
            desiredRotation = getDesiredHeading,
            outputModuleStates = swerveDrive.runSwerveModuleStates,
            requirements = swerveDrive
        )
        self.swerveDrive = swerveDrive
        self.getWaypoints = getWaypoints

        self.setName( "DriveToPath" )
        self.addRequirements( self.swerveDrive )

    def initialize(self) -> None:
        trajGen = TrajectoryGenerator()
        trajCfg = TrajectoryConfig( self.swerveDrive.maxVelocity.get(), self.swerveDrive.maxVelocity.get() / 2 )
        trajCfg.setKinematics( self.swerveDrive.getKinematics() )

        traj = trajGen.generateTrajectory(
            waypoints = self.getWaypoints(),
            config = trajCfg
        )

        self.m_trajectory = traj
        self.m_controller.getThetaController().reset(
            self.swerveDrive.getRobotAngle().radians(),
            self.swerveDrive.getRotationVelocity()
        )
        return super().initialize()

