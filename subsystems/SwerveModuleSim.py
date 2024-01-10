"""
Description: Swerve Module Container Class
Version:  1
Date:  2024-01-03
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

from .SwerveModule import SwerveModule
from util import *

loopTime = 0.02

# Class: SwerveModule
class SwerveModuleSim(SwerveModule):

    def __init__(self, subsystemName:str, posX:float, posY:float): #, angleOffset:float):
        self.name = subsystemName

        # Wheel Constraints
        self.driveGearRatio = NTTunableFloat( "SwerveModule/Drive/GearRatio", 1 / 6.75, self.updateDriveEncoderConversions ) # ( L1: 8.14:1 | L2: 6.75:1 | L3: 6.12:1 )
        self.angleGearRatio = NTTunableFloat( "SwerveModule/Angle/GearRatio", 1 / (150/7), self.updateAngleEncoderConversions ) # 150/7:1
        self.wheelRadius = NTTunableFloat( "SwerveModule/Drive/wheelRadius", 0.0508, self.updateDriveEncoderConversions ) # In Meters

        # Drive Motor PID Values
        self.driveSmart = NTTunableBoolean( "SwerveModule/Drive/smartMotion", False )
        self.drive_kP = NTTunableFloat( "SwerveModule/Drive/PID/kP", 0.05, self.updateDrivePIDController ) #0.04
        self.drive_kI = NTTunableFloat( "SwerveModule/Drive/PID/kI", 0.0, self.updateDrivePIDController )
        self.drive_kD = NTTunableFloat( "SwerveModule/Drive/PID/kD", 0.0, self.updateDrivePIDController ) #1.0
        self.drive_kF = NTTunableFloat( "SwerveModule/Drive/PID/kF", 0.0, self.updateDrivePIDController ) #0.065
        self.drive_kS = NTTunableFloat( "SwerveModule/Drive/FF/kS", 0.0, self.updateDrivePIDController )
        self.drive_kV = NTTunableFloat( "SwerveModule/Drive/FF/kV", 0.0, self.updateDrivePIDController )
        self.drive_kIZone = NTTunableFloat( "SwerveModule/Drive/PID/IZone", 0.0, self.updateDrivePIDController )
        self.drive_kError = NTTunableFloat( "SwerveModule/Drive/PID/Error", 0.0, self.updateDrivePIDController )
        self.drive_kSlotIdx = NTTunableInt( "SwerveModule/Drive/PID/kSlotIdx", 0, self.updateDrivePIDController )
        self.drive_mmMaxVelocity = NTTunableInt( "SwerveModule/Drive/PID/smartVelocity", 20480, self.updateDrivePIDController )
        self.drive_mmMaxAcceleration = NTTunableInt( "SwerveModule/Drive/PID/smartAccel", 4 * self.drive_mmMaxVelocity.get(), self.updateDrivePIDController )

        # Angle Motor PID Values
        self.angleSmart = NTTunableBoolean( "SwerveModule/Angle/smartMotion", False )
        self.angle_kP = NTTunableFloat( "SwerveModule/Angle/PID/kP", 10, self.updateAnglePIDController ) #0.5
        self.angle_kI = NTTunableFloat( "SwerveModule/Angle/PID/kI", 0, self.updateAnglePIDController )
        self.angle_kD = NTTunableFloat( "SwerveModule/Angle/PID/kD", 0, self.updateAnglePIDController )
        self.angle_kF = NTTunableFloat( "SwerveModule/Angle/PID/kF", 0, self.updateAnglePIDController )
        self.angle_kIZone = NTTunableFloat( "SwerveModule/Angle/PID/IZone", 0.0, self.updateAnglePIDController )
        self.angle_kError = NTTunableFloat( "SwerveModule/Angle/PID/Error", 0.0, self.updateAnglePIDController )
        self.angle_kSlotIdx = NTTunableInt( "SwerveModule/Angle/PID/kSlotIdx", 0, self.updateAnglePIDController )
        self.angle_mmMaxVelocity = NTTunableInt( "SwerveModule/Angle/PID/smartVelocity", 2048, self.updateAnglePIDController )
        self.angle_mmMaxAcceleration = NTTunableInt( "SwerveModule/Angle/PID/smartAccel", 2 * self.angle_mmMaxVelocity.get(), self.updateAnglePIDController )

        # Create Motors
        self.driveSim = FlywheelSim( DCMotor.NEO(2), 1 / self.driveGearRatio.get(), 0.025 )
        self.turnSim = FlywheelSim( DCMotor.NEO(1), 1 / self.angleGearRatio.get(), 0.004 )

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
        self.updateAnglePIDController()

        ### Swerve Module Information
        self.setReferencePosition( posX, posY )
        self.moduleState = SwerveModuleState( 0, Rotation2d(0) )

    def updateOutputs(self):
        """
        Update Network Table Logging
        """
        self.driveSim.update( loopTime )
        self.turnSim.update( loopTime )

        # Get Logging Table
        tbl = NetworkTableInstance.getDefault().getTable( f"SysOutputs/SwerveDrive/Module{self.name}" )

        self.driveRelativePosition += self.driveSim.getAngularVelocity() * loopTime
        self.turnRelativePositionRad += self.turnSim.getAngularVelocity() * loopTime
        self.turnRelativePositionDeg += units.radiansToDegrees( self.turnSim.getAngularVelocity() * loopTime )

        # Drive Motor Data
        tbl.putNumber( "drivePositionRad", self.driveRelativePosition )
        tbl.putNumber( "driveVelocityRadPerSec", self.driveSim.getAngularVelocity() )
        tbl.putNumber( "driveAppliedVolts", self.driveAppliedVolts )
        tbl.putNumber( "driveCurrentAmps", abs( self.driveSim.getCurrentDraw() ) )
        tbl.putNumber( "driveTempCelcius", 0.0 )

        # Turn Motor Data
        tbl.putNumber( "turnCanCoder-Relative", 0.0 )
        tbl.putNumber( "turnCanCoder-Absolute", self.turnAbsolutePosition )
        tbl.putNumber( "turnPositionRad", self.turnRelativePositionRad )
        tbl.putNumber( "turnVelocityRadPerSec", self.turnSim.getAngularVelocity() )
        tbl.putNumber( "turnPositionDeg", self.turnRelativePositionDeg )
        tbl.putNumber( "turnVelocityDegPerSec", units.radiansToDegrees( self.turnSim.getAngularVelocity() ) )
        tbl.putNumber( "turnAppliedVolts", self.turnAppliedVolts )
        tbl.putNumber( "turnCurrentAmps", abs( self.turnSim.getCurrentDraw() ) )
        tbl.putNumber( "turnTempCelcius", 0.0 )


    def updateDriveEncoderConversions(self): return None
    def updateAngleEncoderConversions(self): return None

    def updateDrivePIDController(self):
        """
        """
        # Drive Integrated PID Controller
        self.drivePID = PIDController( self.drive_kP.get(), self.drive_kI.get(), self.drive_kD.get(), loopTime )
        self.drivePID.setIZone( self.drive_kIZone.get() )
        self.driveFF = SimpleMotorFeedforwardMeters( self.drive_kS.get(), self.drive_kV.get() )

    def updateAnglePIDController(self):
        """
        """
        # Angle Integrated PID Controller
        self.turnPID = PIDController( self.angle_kP.get(), self.angle_kI.get(), self.angle_kD.get(), loopTime )
        self.turnPID.setIZone( self.angle_kIZone.get() )
        self.turnPID.enableContinuousInput( -math.pi, math.pi )

    def setDriveVelocity(self, velocity:float = 0.0) -> None:
        velocityRadPerSec = velocity / self.wheelRadius.get()
        calcPid = self.drivePID.calculate( self.driveSim.getAngularVelocity(), velocityRadPerSec ) 
        calcFf = self.driveFF.calculate( velocityRadPerSec )
        self.driveAppliedVolts = calcPid + calcFf
        self.driveAppliedVolts = min( max( self.driveAppliedVolts, -12.0 ), 12.0 )
        self.driveAppliedVolts = applyDeadband( self.driveAppliedVolts, 0.04 )
        self.driveSim.setInputVoltage( self.driveAppliedVolts )

    def setTurnPosition(self, rotation:Rotation2d) -> None:
        self.turnAppliedVolts = self.turnPID.calculate( self.turnRelativePositionRad, rotation.radians() )
        self.turnAppliedVolts = min( max( self.turnAppliedVolts, -12.0 ), 12.0 )
        self.turnAppliedVolts = applyDeadband( self.turnAppliedVolts, 0.005 )
        self.turnSim.setInputVoltage( self.turnAppliedVolts )

    def getModulePosition(self) -> SwerveModulePosition:
        """
        Get the Current Position of this Module in Meters and Rotation2d

        :returns SwerveModuleState
        """
        self.modulePosition = SwerveModulePosition(
            units.radiansToRotations( self.driveRelativePosition ) * self.driveGearRatio.get() / self.wheelRadius.get(),
            Rotation2d( self.turnRelativePositionRad )
        )
        return self.modulePosition #super().getModulePosition()


