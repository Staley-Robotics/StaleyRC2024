"""
Description: Swerve Module (West Coast Products - Swerve X)
Version:  1
Date:  2024-01-05

Drive Motor Controllers:  REV NEO 
Angle Motor Controllers:  REV NEO
Angle Sensors:  CAN CODERS

Velocity: Closed Loop (SparkMAX Integrated)
Angle:  Closed Loop (SparkMAX Integrated)
"""

### Imports
# Python Imports
import math

# FRC Component Imports
from ctre.sensors import WPI_CANCoder, SensorInitializationStrategy, AbsoluteSensorRange
from rev import * #CANSparkMax, SparkMaxPIDController, SparkMaxAlternateEncoder, SparkMaxAbsoluteEncoder, AbsoluteEncoder, RelativeEncoder
from ntcore import NetworkTableInstance
from wpilib import RobotBase
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
from wpimath.geometry import Translation2d, Rotation2d

# Self Made Classes
from .SwerveModule import SwerveModule
from util import *

# Class: SwerveModule
class SwerveModuleNeo(SwerveModule):
    driveMotor:CANSparkMax = None
    angleMotor:CANSparkMax = None
    angleSensor:WPI_CANCoder = None

    referencePosition:Translation2d = None
    moduleState:SwerveModuleState = None

    def __init__(self, subsystemName, driveId, angleId, sensorId, posX, posY, angleOffset):
        ### Module Name
        self.name = subsystemName

        ### Tunable Variables
        # Encoder Conversions
        self.driveGearRatio = NTTunableFloat( "SwerveModule/Drive/GearRatio", 1 / 6.75, self.updateDriveEncoderConversions ) # ( L1: 8.14:1 | L2: 6.75:1 | L3: 6.12:1 )
        self.wheelRadius = NTTunableFloat( "SwerveModule/Drive/wheelRadius", 0.0508, self.updateDriveEncoderConversions ) # In Meters
        self.angleGearRatio = NTTunableFloat( "SwerveModule/Angle/GearRatio", 1 / (150/7), self.updateAngleEncoderConversions ) # 150/7:1

        # Drive Motor PID Values
        self.driveSmart = NTTunableBoolean( "SwerveModule/Drive/smartMotion", False )
        self.drive_kP = NTTunableFloat( "SwerveModule/Drive/PID/kP", 0.0, self.updateDrivePIDController ) #0.04
        self.drive_kI = NTTunableFloat( "SwerveModule/Drive/PID/kI", 0.0, self.updateDrivePIDController )
        self.drive_kD = NTTunableFloat( "SwerveModule/Drive/PID/kD", 0.0, self.updateDrivePIDController ) #1.0
        self.drive_kF = NTTunableFloat( "SwerveModule/Drive/PID/kF", 0.0, self.updateDrivePIDController ) #0.065
        self.drive_kIZone = NTTunableFloat( "SwerveModule/Drive/PID/IZone", 0.0, self.updateDrivePIDController )
        self.drive_kError = NTTunableFloat( "SwerveModule/Drive/PID/Error", 0.0, self.updateDrivePIDController )
        self.drive_kSlotIdx = NTTunableInt( "SwerveModule/Drive/PID/kSlotIdx", 0, self.updateDrivePIDController )
        self.drive_mmMaxVelocity = NTTunableInt( "SwerveModule/Drive/PID/smartVelocity", 20480, self.updateDrivePIDController )
        self.drive_mmMaxAcceleration = NTTunableInt( "SwerveModule/Drive/PID/smartAccel", 4 * self.drive_mmMaxVelocity.get(), self.updateDrivePIDController )

        # Angle Motor PID Values
        self.angleSmart = NTTunableBoolean( "SwerveModule/Angle/smartMotion", False )
        self.angle_kP = NTTunableFloat( "SwerveModule/Angle/PID/kP", 0, self.updateAnglePIDController ) #0.5
        self.angle_kI = NTTunableFloat( "SwerveModule/Angle/PID/kI", 0, self.updateAnglePIDController )
        self.angle_kD = NTTunableFloat( "SwerveModule/Angle/PID/kD", 0, self.updateAnglePIDController )
        self.angle_kF = NTTunableFloat( "SwerveModule/Angle/PID/kF", 0, self.updateAnglePIDController )
        self.angle_kIZone = NTTunableFloat( "SwerveModule/Angle/PID/IZone", 0.0, self.updateAnglePIDController )
        self.angle_kError = NTTunableFloat( "SwerveModule/Angle/PID/Error", 0.0, self.updateAnglePIDController )
        self.angle_kSlotIdx = NTTunableInt( "SwerveModule/Angle/PID/kSlotIdx", 0, self.updateAnglePIDController )
        self.angle_mmMaxVelocity = NTTunableInt( "SwerveModule/Angle/PID/smartVelocity", 2048, self.updateAnglePIDController )
        self.angle_mmMaxAcceleration = NTTunableInt( "SwerveModule/Angle/PID/smartAccel", 2 * self.angle_mmMaxVelocity.get(), self.updateAnglePIDController )

        ### Angle Sensor
        self.angleSensor = WPI_CANCoder( sensorId ) #, "canivore1")
        self.angleSensor.configFactoryDefault()
        self.angleSensor.configSensorInitializationStrategy(SensorInitializationStrategy.BootToZero)
        self.angleSensor.configAbsoluteSensorRange(AbsoluteSensorRange.Unsigned_0_to_360)
        self.angleSensor.configSensorDirection(False)
        if not RobotBase.isSimulation(): self.angleSensor.setPosition(self.angleSensor.getAbsolutePosition() - angleOffset)

        ### Angle Motor
        self.angleMotor = CANSparkMax( angleId, CANSparkMax.MotorType.kBrushless )    
        self.angleMotor.restoreFactoryDefaults() # Revert to Factory Defaults
        self.angleMotor.setInverted( True )  # WPI_TalonFX.setInverted
        self.angleMotor.setIdleMode( CANSparkMax.IdleMode.kCoast )  # WPI_TalonFX.setNeutralMode
        # WPI_TalonFX.configNeutralDeadband(0.001)  - No equivilant (must be done via CAN or USB)
        
        self.angleMotorEncoder = self.angleMotor.getEncoder() # WPI_TalonFX.configRemoteFeedbackFilter()
        #self.angleMotorEncoder.setInverted(True) # WPI_TalonFX.setSensorPhase()
        self.updateAngleEncoderConversions()
        
        self.angleMotorPid = self.angleMotor.getPIDController()
        self.angleMotorPid.setFeedbackDevice( self.angleMotorEncoder ) # WPI_TalonFX.configSelectedFeedbackSensor()  ### Should this be the CAN Coder?
        self.angleMotorPid.setPositionPIDWrappingEnabled( True ) #WPI_TalonFX.configFeedbackNotContinous()
        self.angleMotorPid.setPositionPIDWrappingMinInput( 0 ) #-180 ) #math.pi )
        self.angleMotorPid.setPositionPIDWrappingMaxInput( 360 ) # 180 ) #math.pi ) 
        self.updateAnglePIDController()     

        # Save Angle Motor Config
        self.angleMotor.burnFlash()

        ### Drive Motor
        self.driveMotor = CANSparkMax( driveId, CANSparkMax.MotorType.kBrushless )
        self.driveMotor.restoreFactoryDefaults()
        self.driveMotor.setInverted( True )
        self.driveMotor.setIdleMode( CANSparkMax.IdleMode.kCoast )
        
        self.driveMotorEncoder = self.driveMotor.getEncoder()
        #self.driveMotorEncoder.setInverted(False)
        self.updateDriveEncoderConversions()

        self.driveMotorPid = self.driveMotor.getPIDController()
        self.driveMotorPid.setFeedbackDevice( self.driveMotorEncoder ) # WPI_TalonFX.configSelectedFeedbackSensor()    
        self.updateDrivePIDController()

        # Save Drive Motor Config
        self.driveMotor.burnFlash()

        ### Swerve Module Information
        self.referencePosition = Translation2d( posX, posY )
        self.moduleState = SwerveModuleState( 0, Rotation2d(0) )

    def updateSysOutputs(self):
        """
        Update Network Table Logging
        """
        # Get Logging Table
        tbl = NetworkTableInstance.getDefault().getTable( f"SysOutputs/SwerveDrive/Module{self.name}" )

        # Drive Motor Data
        tbl.putNumber( "drivePositionRad", self.driveMotorEncoder.getPosition() )
        tbl.putNumber( "driveVelocityRadPerSec", self.driveMotorEncoder.getVelocity() )
        tbl.putNumber( "driveAppliedVolts", self.driveMotor.getAppliedOutput() * self.driveMotor.getBusVoltage() )
        tbl.putNumber( "driveCurrentAmps", self.driveMotor.getOutputCurrent() )
        tbl.putNumber( "driveTempCelcius", self.driveMotor.getMotorTemperature() )

        # Turn Motor Data
        tbl.putNumber( "turnCanCoder-Relative", self.angleSensor.getPosition() )
        tbl.putNumber( "turnCanCoder-Absolute", self.angleSensor.getAbsolutePosition() )
        tbl.putNumber( "turnPositionRad", self.angleMotorEncoder.getPosition() )
        tbl.putNumber( "turnVelocityRadPerSec", self.angleMotorEncoder.getVelocity() )
        tbl.putNumber( "turnAppliedVolts", self.angleMotor.getAppliedOutput() * self.angleMotor.getBusVoltage() )
        tbl.putNumber( "turnCurrentAmps", self.angleMotor.getOutputCurrent() )
        tbl.putNumber( "turnTempCelcius", self.angleMotor.getMotorTemperature() )

    def updateDriveEncoderConversions(self):
        """
        """
        driveToMeters = self.driveGearRatio.get() * 2 * math.pi * self.wheelRadius.get()
        self.driveMotorEncoder.setPositionConversionFactor( driveToMeters ) # Meters
        self.driveMotorEncoder.setVelocityConversionFactor( driveToMeters / 60 ) # Meters per Second

    def updateAngleEncoderConversions(self):
        """
        """
        angleToRadians = self.angleGearRatio.get() * 2 * math.pi
        angleToDegrees = self.angleGearRatio.get() * 360
        self.angleMotorEncoder.setPositionConversionFactor( angleToDegrees ) # Radians
        self.angleMotorEncoder.setVelocityConversionFactor( angleToDegrees / 60 ) # Radians per Second
        self.angleMotorEncoder.setPosition( self.angleSensor.getPosition() )

    def updateDrivePIDController(self):
        """
        """
        # Get Slot Index
        slotIdx = self.drive_kSlotIdx.get()

        # Drive Integrated PID Controller
        self.driveMotorPid.setP( self.drive_kP.get(), slotIdx ) # TalonFX.config_kP()
        self.driveMotorPid.setI( self.drive_kI.get(), slotIdx ) # TalonFX.config_kI()
        self.driveMotorPid.setIZone( self.drive_kIZone.get(), slotIdx ) # TalonFX.config_IntegralZone()
        self.driveMotorPid.setD( self.drive_kD.get(), slotIdx ) # TalonFX.config_kD()
        self.driveMotorPid.setFF( self.drive_kF.get(), slotIdx ) # TalonFX.config_kF()

        # Drive Integrated PID - Motion Magic Properties
        self.driveMotorPid.setSmartMotionMaxVelocity( self.drive_mmMaxVelocity.get(), slotIdx ) # TalonFX.configMotionCruiseVelocity()
        self.driveMotorPid.setSmartMotionMaxAccel( self.drive_mmMaxAcceleration.get(), slotIdx ) # TalonFX.configMotionAcceleration
        self.driveMotorPid.setSmartMotionAccelStrategy( SparkMaxPIDController.AccelStrategy.kTrapezoidal, slotIdx ) # TalonFX.configMotionSCurveStrength
        self.driveMotorPid.setSmartMotionAllowedClosedLoopError( self.drive_kError.get(), slotIdx ) #TalonFX.configAllowableClosedloopError()

    def updateAnglePIDController(self):
        """
        """
        # Get Slot Index
        slotIdx = self.angle_kSlotIdx.get()

        # Angle Integrated PID Controller
        self.angleMotorPid.setP( self.angle_kP.get(), slotIdx ) # TalonFX.config_kP()
        self.angleMotorPid.setI( self.angle_kI.get(), slotIdx ) # TalonFX.config_kI()
        self.angleMotorPid.setIZone( self.angle_kIZone.get(), slotIdx ) # TalonFX.config_IntegralZone()
        self.angleMotorPid.setD( self.angle_kD.get(), slotIdx ) # TalonFX.config_kD()
        self.angleMotorPid.setFF( self.angle_kF.get(), slotIdx ) # TalonFX.config_kF()

        # Angle Integrated PID - Smart Motion Properties
        self.angleMotorPid.setSmartMotionMaxVelocity( self.angle_mmMaxVelocity.get(), slotIdx ) # TalonFX.configMotionCruiseVelocity()
        self.angleMotorPid.setSmartMotionMaxAccel( self.angle_mmMaxAcceleration.get(), slotIdx ) # TalonFX.configMotionAcceleration
        self.angleMotorPid.setSmartMotionAccelStrategy( SparkMaxPIDController.AccelStrategy.kTrapezoidal, slotIdx ) # TalonFX.configMotionSCurveStrength
        self.angleMotorPid.setSmartMotionAllowedClosedLoopError( self.angle_kError.get(), slotIdx ) #TalonFX.configAllowableClosedloopError()

    def setDesiredState(self, desiredState:SwerveModuleState) -> SwerveModuleState:
        """
        Set the Desired State of this Module in Velocity and Degrees.  This method will optimize 
        the direction / angle needed for fastest response

        :param desiredState is a SwerveModuleState in Meters Per Second and Rotation2d
        """
        ### Calculate / Optimize
        currentAnglePosition = self.angleSensor.getPosition()
        currentAngleRotation = Rotation2d(0).fromDegrees(currentAnglePosition)
        optimalState:SwerveModuleState = SwerveModuleState.optimize(
            desiredState,
            currentAngleRotation
        )
        self.moduleState = optimalState

        # Velocity Smoothing
        velocity = optimalState.speed
        #velocity *= ( optimalState.angle - currentAngleRotation ).cos() # Scale Speed / Smooth rotation ??? Smart Motion?

        # Set Velocity
        velocMode = CANSparkMax.ControlType.kVelocity #if not self.driveSmart.get() else CANSparkMax.ControlType.kSmartVelocity
        self.driveMotorPid.setReference( velocity, velocMode, self.drive_kSlotIdx.get() )

        # Set Angle
        angleMode = CANSparkMax.ControlType.kPosition #if not self.angleSmart.get() else CANSparkMax.ControlType.kSmartMotion
        self.angleMotorPid.setReference( optimalState.angle.degrees(), angleMode, self.angle_kSlotIdx.get() )

        return optimalState

    def getReferencePosition(self) -> Translation2d:
        """
        Get the Reference Position of this Module on the SwerveDrive in (x,y) coordinates 
        where x is forward and y is left

        :returns Translation2d
        """
        return self.referencePosition
       
    def getModuleState(self) -> SwerveModuleState:
        """
        Get the Current State of this Module in Meters Per Second and Rotation2d

        :returns SwerveModuleState
        """
        return self.moduleState

    def getModulePosition(self) -> SwerveModulePosition:
        """
        Get the Current Module Position in Meters Per Second and Rotation2d

        :returns SwerveModulePosition object
        """
        return SwerveModulePosition(
            distance=self.driveMotorEncoder.getPosition(),
            angle=Rotation2d( self.angleMotorEncoder.getPosition() )
        )

