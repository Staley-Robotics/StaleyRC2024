import typing

from commands2 import Command, Subsystem
from wpimath.controller import HolonomicDriveController, PIDController, ProfiledPIDController
from wpimath.geometry import Pose2d, Rotation2d
from wpimath.kinematics import SwerveDrive4Kinematics, SwerveModuleState
from wpimath.trajectory import Trajectory
from wpilib import Timer

class Swerve4ControllerCommand(Command):
    m_timer:Timer = Timer()
    m_trajectory:Trajectory = None
    m_pose:typing.Callable[[],Pose2d] = lambda: None
    m_kinematics:SwerveDrive4Kinematics = None
    m_controller:HolonomicDriveController = None
    m_outputModuleStates:typing.Callable[[typing.Tuple[SwerveModuleState,SwerveModuleState,SwerveModuleState,SwerveModuleState]], None] = lambda: None
    m_desiredRotation:typing.Callable[[],Rotation2d] = lambda: None

    @typing.overload
    def __init__( self,
                  trajectory:Trajectory, 
                  pose:typing.Callable[[],Pose2d],  
                  kinematics:SwerveDrive4Kinematics, 
                  xController:PIDController, 
                  yController:PIDController, 
                  thetaController:ProfiledPIDController, 
                  desiredRotation:typing.Callable[[],Rotation2d], 
                  outputModuleStates:typing.Callable[[typing.Tuple[SwerveModuleState,SwerveModuleState,SwerveModuleState,SwerveModuleState]], None], 
                  requirements:Subsystem
    ):
        self.__init__(
            trajectory,
            pose,
            kinematics,
            HolonomicDriveController(
                xController,
                yController,
                thetaController
            ),
            desiredRotation,
            outputModuleStates,
            requirements
        )

    @typing.overload
    def __init__( self,
                  trajectory:Trajectory, 
                  pose:typing.Callable[[],Pose2d],  
                  kinematics:SwerveDrive4Kinematics, 
                  xController:PIDController, 
                  yController:PIDController, 
                  thetaController:ProfiledPIDController, 
                  outputModuleStates:typing.Callable[[typing.Tuple[SwerveModuleState,SwerveModuleState,SwerveModuleState,SwerveModuleState]], None], 
                  requirements:Subsystem
    ):
        self.__init__(
            trajectory,
            pose,
            kinematics,
            HolonomicDriveController(
                xController,
                yController,
                thetaController
            ),
            lambda: trajectory.states()[len(trajectory.states())-1].pose.rotation(),
            outputModuleStates,
            requirements
        )

    @typing.overload
    def __init__( self,
                  trajectory:Trajectory, 
                  pose:typing.Callable[[],Pose2d],  
                  kinematics:SwerveDrive4Kinematics, 
                  controller:HolonomicDriveController, 
                  outputModuleStates:typing.Callable[[typing.Tuple[SwerveModuleState,SwerveModuleState,SwerveModuleState,SwerveModuleState]], None], 
                  requirements:Subsystem
    ):
        self.__init__(
            trajectory,
            pose,
            kinematics,
            controller,
            lambda: trajectory.states()[len(trajectory.states())-1].pose.rotation(),
            outputModuleStates,
            requirements
        )

    #@typing.overload # Exclude This overload... final release
    def __init__( self,
                  trajectory:Trajectory, 
                  pose:typing.Callable[[],Pose2d],  
                  kinematics:SwerveDrive4Kinematics, 
                  controller:HolonomicDriveController, 
                  desiredRotation:typing.Callable[[],Rotation2d], 
                  outputModuleStates:typing.Callable[[typing.Tuple[SwerveModuleState,SwerveModuleState,SwerveModuleState,SwerveModuleState]], None], 
                  requirements:Subsystem
    ):
        self.m_trajectory = trajectory
        self.m_pose = pose
        self.m_kinematics = kinematics
        self.m_controller = controller
        self.m_desiredRotation = desiredRotation
        self.m_outputModuleStates = outputModuleStates

        self.setName( "Swerve4ControllerCommand" )
        self.addRequirements( requirements )

    def initialize(self) -> None:
        self.m_timer.restart()

    def execute(self) -> None:
        curTime = self.m_timer.get()
        desiredState = self.m_trajectory.sample(curTime)

        targetChassisSpeeds = self.m_controller.calculate(
            self.m_pose(),
            desiredState,
            self.m_desiredRotation()
        )
        targetModuleState = self.m_kinematics.toSwerveModuleStates(targetChassisSpeeds)
        self.m_outputModuleStates( targetModuleState )

    def end(self, interrupted:bool) -> None:
        self.m_timer.stop()

    def isFinished(self) -> bool:
        return self.m_timer.hasElapsed( self.m_trajectory.totalTime() )