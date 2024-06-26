"""
Description: Swerve Module Container Class
Version:  1
Date:  2024-01-09
"""

### Imports
import typing
import dataclasses

# FRC Component Imports
from wpimath.geometry import Translation2d, Rotation2d, Pose2d
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
import wpiutil.wpistruct
from util import *

# Class: SwerveModule
class SwerveModuleIO:
    """
    Custom SwerveModule Abstract Class used to extend a SwerveModule with our logging capabilities
    """

    @wpiutil.wpistruct.make_wpistruct(name="SwerveModuleIOInputs")
    @dataclasses.dataclass
    class SwerveModuleIOInputs:
        """
        A WPIStruct Object that contains all SwerveModule Data.
        This is intended to simplify logging of this data.
        """
        drivePosition: float = 0
        driveVelocity: float = 0
        driveAppliedVolts: float = 0
        driveCurrentAmps: float = 0
        driveTempCelcius: float = 0

        turnCanCoderRelative: float = 0
        turnCanCoderAbsolute: float = 0
        
        turnPosition: float = 0
        turnVelocity: float = 0
        turnAppliedVolts: float = 0
        turnCurrentAmps: float = 0
        turnTempCelcius: float = 0

    referencePosition:Translation2d = Translation2d(0,0)
    modulePosition:SwerveModulePosition = SwerveModulePosition( 0, Rotation2d() )
    moduleState:SwerveModuleState = SwerveModuleState( 0, Rotation2d() )
    moduleSetpoint:SwerveModuleState = SwerveModuleState( 0, Rotation2d() )

    def __init__(self) -> None:
        # Encoder Conversions
        self.wheelRadius = NTTunableFloat( "SwerveModule/Drive/wheelRadius", 0.0508, self.updateDriveEncoderConversions, persistent=True ) # In Meters
        self.driveGearRatio = NTTunableFloat( "SwerveModule/Drive/GearRatio", 1 / 6.75, self.updateDriveEncoderConversions, persistent=True ) # ( L1: 8.14:1 | L2: 6.75:1 | L3: 6.12:1 )
        self.turnGearRatio = NTTunableFloat( "SwerveModule/Turn/GearRatio", 1 / (150/7), self.updateTurnEncoderConversions, persistent=True ) # 150/7:1

        # Drive Motor PID Values
        self.drive_kP = NTTunableFloat( "SwerveModule/DrivePID/kP", 0.0, self.updateDrivePIDController, persistent=True ) #0.04
        self.drive_kI = NTTunableFloat( "SwerveModule/DrivePID/kI", 0.0, self.updateDrivePIDController, persistent=True )
        self.drive_kD = NTTunableFloat( "SwerveModule/DrivePID/kD", 0.0, self.updateDrivePIDController, persistent=True ) #1.0
        self.drive_kF = NTTunableFloat( "SwerveModule/DrivePID/kF", 0.22, self.updateDrivePIDController, persistent=True ) #0.065
        self.drive_kIZone = NTTunableFloat( "SwerveModule/DrivePID/IZone", 0.0, self.updateDrivePIDController, persistent=True )
        self.drive_kError = NTTunableFloat( "SwerveModule/DrivePID/Error", 0.0, self.updateDrivePIDController, persistent=True )

        # Turn Motor PID Values
        self.turn_kP = NTTunableFloat( "SwerveModule/TurnPID/kP", 0.01, self.updateTurnPIDController, persistent=True ) #0.5
        self.turn_kI = NTTunableFloat( "SwerveModule/TurnPID/kI", 0, self.updateTurnPIDController, persistent=True )
        self.turn_kD = NTTunableFloat( "SwerveModule/TurnPID/kD", 0, self.updateTurnPIDController, persistent=True )
        self.turn_kF = NTTunableFloat( "SwerveModule/TurnPID/kF", 0, self.updateTurnPIDController, persistent=True )
        self.turn_kIZone = NTTunableFloat( "SwerveModule/TurnPID/IZone", 0.0, self.updateTurnPIDController, persistent=True )
        self.turn_kError = NTTunableFloat( "SwerveModule/TurnPID/Error", 0.0, self.updateTurnPIDController, persistent=True )

    def updateDriveEncoderConversions(self):
        """
        Update the Onboard Position and Velocity Conversions with the Drive Motor
        """
        pass

    def updateTurnEncoderConversions(self):
        """
        Update the Onboard Position and Velocity Conversions with the Turn Motor
        """
        pass

    def updateDrivePIDController(self):
        """
        Update the PID Controller for the Drive Motor
        """
        pass

    def updateTurnPIDController(self):
        """
        Update the PID Controller for the Turn Motor
        """
        pass
    
    def updateInputs(self, inputs:SwerveModuleIOInputs):
        """
        Update SwerveModuleInputs Values for Logging Purposes
        :param inputs: SwerveModuleInputs objects that need to be updated
        """
        pass

    def run(self):
        """
        Runs this SwerveModule
        """
        self.setDriveVelocity( self.getModuleSetpoint().speed ) # Set Drive Velocity
        self.setTurnPosition( self.getModuleSetpoint().angle ) # Set Turn Position

    def runCharacterization(self, volts:float = 0.0, asRotation:bool = False):
        """
        Runs SwerveModule Characterization Function
        """
        rotation = Rotation2d(0)
        if asRotation:
            rotation = self.getReferencePosition().angle().rotateBy( Rotation2d().fromDegrees(90) )
        self.setDriveVoltage( volts ) # Set Drive Velocity
        self.setTurnPosition( rotation ) # Set Turn Position
    
    def setReferencePosition(self, posX:float = 0.0, posY:float = 0.0) -> None:
        """
        Get the Reference Position of this Module on the SwerveDrive in (x,y) coordinates 
        where x is forward and y is left

        :param posX: front to back position of this SwerveModule in meters (forward positive)
        :param posY: side to side position of this SwerveModule in meters (left positive)
        """
        self.referencePosition = Translation2d( posX, posY )

    def getReferencePosition(self) -> Translation2d:
        """
        Get the Reference Position of this Module on the SwerveDrive in (x,y) coordinates 
        where x is forward and y is left

        :returns Translation2d
        """
        return self.referencePosition

    def setModuleState(self, desiredState:SwerveModuleState, optimize:bool=False):
        """
        Set the Desired State of this Module in Velocity and Degrees.  This method will optimize 
        the direction / angle needed for fastest response

        :param desiredState is a SwerveModuleState in Meters Per Second and Rotation2d
        """
        ### Calculate / Optimize
        if optimize:
            desiredState:SwerveModuleState = SwerveModuleState.optimize(
                desiredState,
                self.getModuleState().angle
            )
        if desiredState.speed == 0:
            desiredState = SwerveModuleState( desiredState.speed, self.getModulePosition().angle )
        self.moduleSetpoint = desiredState # Save SwerveModuleState Globally

    def getModuleState(self) -> SwerveModuleState:
        """
        Get the Current State of this Module in Meters Per Second and Rotation2d

        :returns SwerveModuleState
        """
        return self.moduleState

    def getModuleSetpoint(self) -> SwerveModuleState:
        """
        Get the Desired Setpoint of the State of this Module in Meters Per Second and Rotation2d

        :returns SwerveModuleState
        """
        return self.moduleSetpoint

    def getModulePosition(self) -> SwerveModulePosition:
        """
        Get the Current Position of this Module in Meters and Rotation2d

        :returns SwerveModuleState
        """
        return self.modulePosition

    """
    Functions that must be written with any classes that extend this SwerveModule class
    """
    def setDriveVoltage(self, volts:float = 0.0) -> None:
        """
        Set the current drive velocity in meters per second
        """
        raise NotImplementedError( "SwerveModule.setDriveVelocity() must created in child class." )

    def setDriveVelocity(self, velocity:float = 0.0) -> None:
        """
        Set the current drive velocity in meters per second

        :param velocity: velocity (meters per second)
        """
        raise NotImplementedError( "SwerveModule.setDriveVelocity() must created in child class." )
    
    def setTurnPosition(self, rotation:Rotation2d = Rotation2d()) -> None:
        """
        Set the current Turning Motor position based on Rotation

        :param rotation: rotation (Rotation2d)
        """
        raise NotImplementedError( "SwerveModule.setTurnPosition() must be created in child class." )
        
