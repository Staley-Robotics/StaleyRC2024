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
from .SwerveModuleIO import SwerveModuleIO
from util import *

loopTime = 0.02

# Class: SwerveModule
class SwerveModuleIOSim(SwerveModuleIO):
    """
    Custom SwerveModuleSim used to simulation the NEO motor without a live robot
    """

    def __init__(self, subsystemName:str, posX:float, posY:float): #, turnOffset:float):
        """
        Initialization
        """
        ### Module Name
        super().__init__()
        self.name = subsystemName

        self.drive_kS = NTTunableFloat( "SwerveModule/DrivePID/kS", 0, self.updateDrivePIDController ) #0.065
        self.drive_kV = NTTunableFloat( "SwerveModule/DrivePID/kV", 0.22, self.updateDrivePIDController ) #0.065
        self.drive_kA = NTTunableFloat( "SwerveModule/DrivePID/kA", 0, self.updateDrivePIDController ) #0.065

        # Create Motors
        self.driveSim = FlywheelSim( DCMotor.NEO(1), 1 / self.driveGearRatio.get(), 0.060 )
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

    def updateInputs(self, inputs:SwerveModuleIO.SwerveModuleIOInputs):
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
        inputs.drivePosition =  self.driveRelativePosition * self.wheelRadius.get()
        inputs.driveVelocity = self.driveSim.getAngularVelocity() * self.wheelRadius.get()
        inputs.driveAppliedVolts = self.driveAppliedVolts
        inputs.driveCurrentAmps = abs( self.driveSim.getCurrentDraw() )
        inputs.driveTempCelcius = 0.0

        # Turn Encoder Data
        inputs.turnCanCoderRelative = 0.0
        inputs.turnCanCoderAbsolute = self.turnAbsolutePosition
        
        # Turn Motor Data
        inputs.turnVelocity = units.radiansToDegrees( self.turnSim.getAngularVelocity() )
        inputs.turnPosition = self.turnRelativePositionDeg
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
        self.drivePID = PIDController( self.drive_kP.get(), self.drive_kI.get(), self.drive_kD.get() )
        self.drivePID.setIZone( self.drive_kIZone.get() )
        self.driveFF = SimpleMotorFeedforwardMeters( self.drive_kS.get(), self.drive_kV.get() )

    def updateTurnPIDController(self):
        """
        Update the PID Controller for the Turn Motor
        """
        # Turn Integrated PID Controller
        self.turnPID = PIDController( self.turn_kP.get(), self.turn_kI.get(), self.turn_kD.get() )
        self.turnPID.setIZone( self.turn_kIZone.get() )
        self.turnPID.enableContinuousInput( -180, 180 ) #-math.pi, math.pi )

    def setDriveVoltage(self, volts:float = 0.0) -> None:
        """
        Set the current drive motor voltage in volts

        :param volts: motor voltage (range -12.0 -> 12.0)
        """
        volts = min( max( volts, -12.0 ), 12.0 )
        #volts = applyDeadband( volts, 0.001 * 12, 12.0 ) # 0.1% Deadband on Motor Voltage
        self.driveSim.setInputVoltage( volts )
        self.driveAppliedVolts = volts

    def setTurnVoltage(self, volts:float = 0.0) -> None:
        """
        Set the current turn motor voltage in volts
        
        :param volts: motor voltage (range -12.0 -> 12.0)
        """
        volts = min( max( volts, -12.0 ), 12.0 )
        #volts = applyDeadband( volts, 0.04 * 12, 12.0 ) # 4% Deadband on Motor Voltage
        self.turnSim.setInputVoltage( volts )
        self.turnAppliedVolts = volts

    def setDriveVelocity(self, velocity:float = 0.0) -> None:
        """
        Set the current drive velocity in meters per second

        :param velocity: velocity (meters per second)
        """
        curVeloc = self.driveSim.getAngularVelocity() * self.wheelRadius.get()
        calcPid = self.drivePID.calculate( curVeloc, velocity ) 
        calcFf = self.driveFF.calculate( velocity )
        calc = calcPid + calcFf
        calc = min( max( calc, -1.0), 1.0 )
        #calc = applyDeadband( calc, 0.001 ) # Velocity Error Range:: 0.001 m/s
        self.setDriveVoltage( calc * 12.0 )

    def setTurnPosition(self, rotation:Rotation2d) -> None:
        """
        Set the current Turning Motor position based on Rotation

        :param rotation: rotation (Rotation2d)
        """
        currentDeg = self.turnRelativePositionDeg % 360
        targetDeg = rotation.degrees()
        calcPid = self.turnPID.calculate( currentDeg, rotation.degrees() )
        calcPid = min( max( calcPid, -1.0 ), 1.0 )
        self.setTurnVoltage( calcPid * 12.0 )