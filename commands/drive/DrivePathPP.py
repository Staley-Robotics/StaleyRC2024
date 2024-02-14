# Import Python
import math
import typing

# Import FRC
from commands2 import Command
from wpilib import Timer, DriverStation
from wpimath.kinematics import SwerveDrive4Kinematics, SwerveModuleState
from wpimath.controller import PIDController, ProfiledPIDControllerRadians, HolonomicDriveController
from wpimath.geometry import Translation2d, Pose2d, Rotation2d
from wpimath.trajectory import Trajectory, TrajectoryConfig, TrajectoryGenerator, TrapezoidProfileRadians
from pathplannerlib import *
from pathplannerlib.auto import *
from pathplannerlib.commands import *
from pathplannerlib.config import *
from pathplannerlib.controller import *
from pathplannerlib.geometry_util import *
from pathplannerlib.logging import *
from pathplannerlib.path import *
from pathplannerlib.pathfinders import *
from pathplannerlib.pathfinding import *
from pathplannerlib.telemetry import *
from pathplannerlib.trajectory import *

# Import Subsystems and Commands
from subsystems import SwerveDrive

class DrivePathPP(FollowPathHolonomic):
    def __init__( self, drivetrain:SwerveDrive, waypoints:typing.Callable[[],typing.List[Pose2d]], finalPose:typing.Callable[[],Rotation2d] ):       
        path:PathPlannerPath = PathPlannerPath(
            bezier_points = PathPlannerPath.bezierFromPoses( waypoints() ),
            constraints = PathConstraints(
                maxVelocityMps = 4.25, #drivetrain.maxVelocity.get(),
                maxAccelerationMpsSq = 4.25 / 2, #drivetrain.maxVelocity.get() / 2,
                maxAngularVelocityRps = 2 * math.pi, #drivetrain.maxAngularVelocity.get(),
                maxAngularAccelerationRpsSq = math.pi #drivetrain.maxAngularVelocity.get() / 2
            ),
            goal_end_state = GoalEndState(
                velocity = 0.0,
                rotation = finalPose(),
                rotateFast = True
            ),
            holonomic_rotations = [],
            constraint_zones = [],
            event_markers = [],
            is_reversed = False,
            preview_starting_rotation = Rotation2d()
        )
        pose_supplier:typing.Callable[[],Pose2d] = drivetrain.getPose
        speeds_supplier:typing.Callable[[], ChassisSpeeds] = drivetrain.getChassisSpeeds
        output_robot_relative:typing.Callable[[ChassisSpeeds], None] = drivetrain.runChassisSpeeds
        config: HolonomicPathFollowerConfig = HolonomicPathFollowerConfig(
            translationConstants = PIDConstants(
                3, #drivetrain.getHolonomicDriveController().getXController().getP(),
                drivetrain.getHolonomicDriveController().getXController().getI(),
                drivetrain.getHolonomicDriveController().getXController().getD(),
                drivetrain.getHolonomicDriveController().getXController().getIZone(),
            ),
            rotationConstants= PIDConstants(
                1.2, #drivetrain.getHolonomicDriveController().getThetaController().getP(),
                drivetrain.getHolonomicDriveController().getThetaController().getI(),
                drivetrain.getHolonomicDriveController().getThetaController().getD(),
                drivetrain.getHolonomicDriveController().getThetaController().getIZone(),
            ),
            maxModuleSpeed = drivetrain.maxVelocity.get(),
            driveBaseRadius= math.sqrt( .25 * .25 + .25 * .25 ),
            replanningConfig = ReplanningConfig(
                enableInitialReplanning = True,
                enableDynamicReplanning = False,
                dynamicReplanningTotalErrorThreshold = 1,
                dynamicReplanningErrorSpikeThreshold = 0.25
            ),
            period = 0.02
        )
        should_flip_path: typing.Callable[[], bool] = lambda: False #= lambda: DriverStation.getAlliance() == DriverStation.Alliance.kRed
        #requirements: Subsystem

        super().__init__(
            path,
            pose_supplier,
            speeds_supplier,
            output_robot_relative,
            config,
            should_flip_path,
            drivetrain
        )

        self.setName( "DrivePathPP" )
