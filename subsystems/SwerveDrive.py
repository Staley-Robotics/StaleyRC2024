"""
Description: 4 Wheel Swerve Drive Chassis Container Class
Version:  1
Date:  2024-01-03
"""

### Imports
# Built-In Python
import typing

# FRC Component Imports
from commands2 import Subsystem
from wpilib import SmartDashboard
from wpimath.controller import HolonomicDriveController
from wpimath.geometry import Rotation2d, Pose2d
from wpimath.kinematics import SwerveDrive4Kinematics, ChassisSpeeds, SwerveModuleState
from wpimath.estimator import SwerveDrive4PoseEstimator

### Class: SwerveDrive
class SwerveDrive(Subsystem):
    class BooleanProperty():
        _name:str = ""
        _value:bool = False
        def __init__(self, name:str, value:bool = False) -> None:
            self._name = name
            self.set( value )
        def set(self, value:bool) -> None:
            self._value = value
            SmartDashboard.putBoolean( self._name, value )
        def get(self) -> bool:
            return self._value
        def toggle(self) -> None:
            current = self.get()
            self.set(not current)
    
    # Initialization
    #def __init__(self):
    #    return None

    # Update Odometry Information on each loop
    def periodic(self):
        return None

    def simulationPeriodic(self) -> None:
        return None

    ### Drive Based Functions
    # Stop Drivetrain
    def stop(self): # -> CommandBase:
        return None


    #### Get 
    # PID Controller
    def getHolonomicPIDController(self) -> HolonomicDriveController:
        return None

    # Kinematics
    def getKinematics(self) -> SwerveDrive4Kinematics:
        return None
       
    # Get Odometry Object
    def getOdometry(self) -> SwerveDrive4PoseEstimator:
        return None

    # Get Pose
    def getPose(self) -> Pose2d:
        return None
    
    # Get Heading of Rotation
    def getRobotAngle(self) -> Rotation2d:
        return None

    # Get Rotational Velocity
    def getRotationVelocity(self) -> float:
        return None

    # Get ChassisSpeeds
    def getChassisSpeeds(self) -> ChassisSpeeds:
        return None
    
    ### Run SwerveDrive Functions
    def runPercentageInputs(self, x:float = 0.0, y:float = 0.0, r:float = 0.0) -> None:
        return None

    # Run SwerveDrive using ChassisSpeeds
    def runChassisSpeeds(self, speeds:ChassisSpeeds, convertFieldRelative:bool = False) -> None:
        return None

    # Run SwerveDrive using SwerveModuleStates
    def runSwerveModuleStates(self, states:typing.List[SwerveModuleState]) -> None:
        return None


