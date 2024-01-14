"""
Description: Swerve Module Simulated NEO Class
Version:  1
Date:  2024-01-09
"""

### Imports
# FRC Component Imports
import math
from random import random

from ntcore import NetworkTableInstance
from wpilib.simulation import FlywheelSim
from wpimath.controller import PIDController, SimpleMotorFeedforwardMeters
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
from wpimath.geometry import Translation2d, Rotation2d
from wpimath.system.plant import DCMotor
from wpimath import units, applyDeadband

# Our Imports
from .SwerveModule import SwerveModule
from util import *

loopTime = 0.02

# Class: SwerveModule
class SwerveModuleSim(SwerveModule):
    """
    Custom SwerveModuleSim used to simulation the NEO motor without a live robot
    """

    def __init__(self, subsystemName:str, posX:float, posY:float): #, turnOffset:float):
        """
        Initialization
        """
        ### Module Name
        self.name = subsystemName

        # Wheel Constraints
        self.driveGearRatio = NTTunableFloat( "SwerveModule/Drive/GearRatio", 1 / 6.75, self.updateDriveEncoderConversions ) # ( L1: 8.14:1 | L2: 6.75:1 | L3: 6.12:1 )
        self.turnGearRatio = NTTunableFloat( "SwerveModule/Turn/GearRatio", 1 / (150/7), self.updateTurnEncoderConversions ) # 150/7:1
        self.wheelRadius = NTTunableFloat( "SwerveModule/Drive/wheelRadius", 0.0508, self.updateDriveEncoderConversions ) # In Meters

        # Drive Motor PID Values
        self.driveSmart = NTTunableBoolean( "SwerveModule/Drive/smartMotion", False )
        self.drive_kP = NTTunableFloat( "SwerveModule/Drive/PID/kP", 0.8, self.updateDrivePIDController ) #0.04
        self.drive_kI = NTTunableFloat( "SwerveModule/Drive/PID/kI", 0.0, self.updateDrivePIDController )
        self.drive_kD = NTTunableFloat( "SwerveModule/Drive/PID/kD", 0.0, self.updateDrivePIDController ) #1.0
        self.drive_kF = NTTunableFloat( "SwerveModule/Drive/PID/kF", 0.0, self.updateDrivePIDController ) #0.065
        self.drive_kS = NTTunableFloat( "SwerveModule/Drive/FF/kS", 0.04, self.updateDrivePIDController )
        self.drive_kV = NTTunableFloat( "SwerveModule/Drive/FF/kV", 0.1275, self.updateDrivePIDController )
        self.drive_kIZone = NTTunableFloat( "SwerveModule/Drive/PID/IZone", 0.0, self.updateDrivePIDController )
        self.drive_kError = NTTunableFloat( "SwerveModule/Drive/PID/Error", 0.0, self.updateDrivePIDController )
        self.drive_kSlotIdx = NTTunableInt( "SwerveModule/Drive/PID/kSlotIdx", 0, self.updateDrivePIDController )
        self.drive_mmMaxVelocity = NTTunableInt( "SwerveModule/Drive/PID/smartVelocity", 20480, self.updateDrivePIDController )
        self.drive_mmMaxAcceleration = NTTunableInt( "SwerveModule/Drive/PID/smartAccel", 4 * self.drive_mmMaxVelocity.get(), self.updateDrivePIDController )

        # Turn Motor PID Values
        self.turnSmart = NTTunableBoolean( "SwerveModule/Turn/smartMotion", False )
        self.turn_kP = NTTunableFloat( "SwerveModule/Turn/PID/kP", 10, self.updateTurnPIDController ) #0.5
        self.turn_kI = NTTunableFloat( "SwerveModule/Turn/PID/kI", 0, self.updateTurnPIDController )
        self.turn_kD = NTTunableFloat( "SwerveModule/Turn/PID/kD", 0, self.updateTurnPIDController )
        self.turn_kF = NTTunableFloat( "SwerveModule/Turn/PID/kF", 0, self.updateTurnPIDController )
        self.turn_kIZone = NTTunableFloat( "SwerveModule/Turn/PID/IZone", 0.0, self.updateTurnPIDController )
        self.turn_kError = NTTunableFloat( "SwerveModule/Turn/PID/Error", 0.0, self.updateTurnPIDController )
        self.turn_kSlotIdx = NTTunableInt( "SwerveModule/Turn/PID/kSlotIdx", 0, self.updateTurnPIDController )
        self.turn_mmMaxVelocity = NTTunableInt( "SwerveModule/Turn/PID/smartVelocity", 2048, self.updateTurnPIDController )
        self.turn_mmMaxAcceleration = NTTunableInt( "SwerveModule/Turn/PID/smartAccel", 2 * self.turn_mmMaxVelocity.get(), self.updateTurnPIDController )

        # Create Motors
        self.driveSim = FlywheelSim( DCMotor.NEO(2), 1 / self.driveGearRatio.get(), 0.025 )
        self.turnSim = FlywheelSim( DCMotor.NEO(1), 1 / self.turnGearRatio.get(), 0.004 )

        # Set Drive Motor Sensor Data 
        self.driveRelativePosition = 0.0
        self.driveAppliedVolts = 0.0

        # Set Turn Motor Sensor Data
        self.turnRelativePositionRad = 0.0
        self.turnRelativePositionDeg = 0.0
        self.turnAbsolutePosition = random() * 2.0 * math.pi
        self.turnAppliedVolts = 0.0

        # Update PID Controllers
        self.updateDrivePIDController()
        self.updateTurnPIDController()

        ### Swerve Module Information
        self.setReferencePosition( posX, posY )
        self.moduleState = SwerveModuleState( 0, Rotation2d(0) )

    def updateInputs(self, inputs:SwerveModule.SwerveModuleInputs):
        """
        Update SwerveModuleInputs Values for Logging Purposes
        :param inputs: SwerveModuleInputs objects that need to be updated
        """
        self.driveSim.update( loopTime )
        self.turnSim.update( loopTime )

        self.driveRelativePosition += self.driveSim.getAngularVelocity() * loopTime
        self.turnRelativePositionRad += self.turnSim.getAngularVelocity() * loopTime
        self.turnRelativePositionDeg += units.radiansToDegrees( self.turnSim.getAngularVelocity() * loopTime )

        # Drive Motor Data
        inputs.driveRadPosition = self.driveRelativePosition
        inputs.driveRadPerSecVelocity = self.driveSim.getAngularVelocity()
        inputs.driveMtrsPosition =  self.driveRelativePosition * self.wheelRadius.get()
        inputs.driveMtrsPerSecVelocity = self.driveSim.getAngularVelocity() * self.wheelRadius.get()
        inputs.driveAppliedVolts = self.driveAppliedVolts
        inputs.driveCurrentAmps = abs( self.driveSim.getCurrentDraw() )
        inputs.driveTempCelcius = 0.0

        # Turn Motor Data
        inputs.turnCanCoderRelative = 0.0
        inputs.turnCanCoderAbsolute = self.turnAbsolutePosition
        inputs.turnRadPosition = self.turnRelativePositionRad
        inputs.turnDegPerSecVelocity = units.radiansToDegrees( self.turnSim.getAngularVelocity() )
        inputs.turnDegPosition = units.radiansToDegrees( self.turnRelativePositionRad )
        inputs.turnRadPerSecVelocity = self.turnSim.getAngularVelocity()
        inputs.turnAppliedVolts = self.turnAppliedVolts
        inputs.turnCurrentAmps = abs( self.turnSim.getCurrentDraw() )
        inputs.turnTempCelcius = 0.0

        self.moduleState = SwerveModuleState(
            self.driveSim.getAngularVelocity() * self.wheelRadius.get(),
            Rotation2d( self.turnRelativePositionRad )
        )

        self.modulePosition = SwerveModulePosition(
            self.driveRelativePosition * self.wheelRadius.get(),
            Rotation2d( self.turnRelativePositionRad )
        )

    def updateDriveEncoderConversions(self): return None
    def updateTurnEncoderConversions(self): return None

    def updateDrivePIDController(self):
        """
        Update the PID Controller for the Drive Motor
        """
        # Drive Integrated PID Controller
        self.drivePID = PIDController( self.drive_kP.get(), self.drive_kI.get(), self.drive_kD.get(), loopTime )
        self.drivePID.setIZone( self.drive_kIZone.get() )
        self.driveFF = SimpleMotorFeedforwardMeters( self.drive_kS.get(), self.drive_kV.get() )

    def updateTurnPIDController(self):
        """
        Update the PID Controller for the Turn Motor
        """
        # Turn Integrated PID Controller
        self.turnPID = PIDController( self.turn_kP.get(), self.turn_kI.get(), self.turn_kD.get(), loopTime )
        self.turnPID.setIZone( self.turn_kIZone.get() )
        self.turnPID.enableContinuousInput( -math.pi, math.pi )

    def setDriveVelocity(self, velocity:float = 0.0) -> None:
        """
        Set the current drive velocity in meters per second
        """
        velocityRadPerSec = velocity / self.wheelRadius.get()
        calcPid = self.drivePID.calculate( self.driveSim.getAngularVelocity(), velocityRadPerSec ) 
        calcFf = self.driveFF.calculate( velocityRadPerSec )
        self.driveAppliedVolts = calcPid + calcFf
        self.driveAppliedVolts = min( max( self.driveAppliedVolts, -12.0 ), 12.0 )
        self.driveAppliedVolts = applyDeadband( self.driveAppliedVolts, 0.04 )
        self.driveSim.setInputVoltage( self.driveAppliedVolts )

    def setTurnPosition(self, rotation:Rotation2d) -> None:
        """
        Set the current Turning Motor position based on Rotation
        """
        self.turnAppliedVolts = self.turnPID.calculate( self.turnRelativePositionRad, rotation.radians() )
        self.turnAppliedVolts = min( max( self.turnAppliedVolts, -12.0 ), 12.0 )
        self.turnAppliedVolts = applyDeadband( self.turnAppliedVolts, 0.005 )
        self.turnSim.setInputVoltage( self.turnAppliedVolts )
