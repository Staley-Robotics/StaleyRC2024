"""
Description: Swerve Module (West Coast Products - Swerve X)
Version:  1
Date:  2024-01-09

Drive Motor Controllers:  REV NEO 
Turn Motor Controllers:  REV NEO
Turn Sensors:  CAN CODERS (Phoenix6 API)

Velocity: Closed Loop (SparkMAX Integrated)
Turn:  Closed Loop (SparkMAX Integrated)
"""

### Imports
# Python Imports
import math

# FRC Component Imports
#from ctre.sensors import WPI_CANCoder, SensorInitializationStrategy, AbsoluteSensorRange
from phoenix6 import StatusCode
from phoenix6.configs import CANcoderConfiguration, cancoder_configs
from phoenix6.hardware import CANcoder
from rev import * #CANSparkMax, SparkMaxPIDController, SparkMaxAlternateEncoder, SparkMaxAbsoluteEncoder, AbsoluteEncoder, RelativeEncoder
from ntcore import NetworkTableInstance
from wpilib import RobotBase
from wpimath import units
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
from wpimath.geometry import Translation2d, Rotation2d

# Self Made Classes
from .SwerveModule import SwerveModule
from util import *

# Class: SwerveModule
class SwerveModuleNeoPhx6(SwerveModule):
    """
    Custom SwerveModuleNeoPhx6 using NEO drive and turn motors on a live robot.

    CTRE CANCoders on Phoenix6 Firmware are used for Absolute position on the turn motor.
    """

    driveMotor:CANSparkMax = None
    turnMotor:CANSparkMax = None
    turnSensor:CANcoder = None

    referencePosition:Translation2d = None
    moduleState:SwerveModuleState = None

    def __init__(self, subsystemName, driveId, turnId, sensorId, posX, posY, turnOffset):
        """
        Initialization
        """
        ### Module Name
        self.name = subsystemName

        ### Tunable Variables
        # Encoder Conversions
        self.driveGearRatio = NTTunableFloat( "SwerveModule/Drive/GearRatio", 1 / 6.75, self.updateDriveEncoderConversions ) # ( L1: 8.14:1 | L2: 6.75:1 | L3: 6.12:1 )
        self.wheelRadius = NTTunableFloat( "SwerveModule/Drive/wheelRadius", 0.0508, self.updateDriveEncoderConversions ) # In Meters
        self.turnGearRatio = NTTunableFloat( "SwerveModule/Turn/GearRatio", 1 / (150/7), self.updateTurnEncoderConversions ) # 150/7:1

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

        # Turn Motor PID Values
        self.turnSmart = NTTunableBoolean( "SwerveModule/Turn/smartMotion", False )
        self.turn_kP = NTTunableFloat( "SwerveModule/Turn/PID/kP", 0, self.updateTurnPIDController ) #0.5
        self.turn_kI = NTTunableFloat( "SwerveModule/Turn/PID/kI", 0, self.updateTurnPIDController )
        self.turn_kD = NTTunableFloat( "SwerveModule/Turn/PID/kD", 0, self.updateTurnPIDController )
        self.turn_kF = NTTunableFloat( "SwerveModule/Turn/PID/kF", 0, self.updateTurnPIDController )
        self.turn_kIZone = NTTunableFloat( "SwerveModule/Turn/PID/IZone", 0.0, self.updateTurnPIDController )
        self.turn_kError = NTTunableFloat( "SwerveModule/Turn/PID/Error", 0.0, self.updateTurnPIDController )
        self.turn_kSlotIdx = NTTunableInt( "SwerveModule/Turn/PID/kSlotIdx", 0, self.updateTurnPIDController )
        self.turn_mmMaxVelocity = NTTunableInt( "SwerveModule/Turn/PID/smartVelocity", 2048, self.updateTurnPIDController )
        self.turn_mmMaxAcceleration = NTTunableInt( "SwerveModule/Turn/PID/smartAccel", 2 * self.turn_mmMaxVelocity.get(), self.updateTurnPIDController )

        ### Turn Sensor (Phoenix6)
        cfg = CANcoderConfiguration()
        cfg.magnet_sensor.absolute_sensor_range = cancoder_configs.AbsoluteSensorRangeValue.UNSIGNED_0_TO1
        cfg.magnet_sensor.sensor_direction = cancoder_configs.SensorDirectionValue.COUNTER_CLOCKWISE_POSITIVE 
        self.turnSensor = CANcoder( sensorId, "rio" )
        self.turnSensor.configurator.apply(cfg)
        if not RobotBase.isSimulation():
            self.turnSensor.set_position( self.turnSensor.get_absolute_position().value_as_double - units.degreesToRotations(turnOffset) )

        ### Turn Motor
        self.turnMotor = CANSparkMax( turnId, CANSparkMax.MotorType.kBrushless )    
        self.turnMotor.restoreFactoryDefaults() # Revert to Factory Defaults
        self.turnMotor.setInverted( True )  # WPI_TalonFX.setInverted
        self.turnMotor.setIdleMode( CANSparkMax.IdleMode.kCoast )  # WPI_TalonFX.setNeutralMode
        # WPI_TalonFX.configNeutralDeadband(0.001)  - No equivilant (must be done via CAN or USB)
        
        self.turnMotorEncoder = self.turnMotor.getEncoder() # WPI_TalonFX.configRemoteFeedbackFilter()
        #self.turnMotorEncoder.setInverted(True) # WPI_TalonFX.setSensorPhase()
        self.updateTurnEncoderConversions()
        
        self.turnMotorPid = self.turnMotor.getPIDController()
        self.turnMotorPid.setFeedbackDevice( self.turnMotorEncoder ) # WPI_TalonFX.configSelectedFeedbackSensor()  ### Should this be the CAN Coder?
        self.turnMotorPid.setPositionPIDWrappingEnabled( True ) #WPI_TalonFX.configFeedbackNotContinous()
        self.turnMotorPid.setPositionPIDWrappingMinInput( 0 ) #-180 ) #math.pi )
        self.turnMotorPid.setPositionPIDWrappingMaxInput( 360 ) # 180 ) #math.pi ) 
        self.updateTurnPIDController()     

        # Save Turn Motor Config
        self.turnMotor.burnFlash()

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
        self.setReferencePosition( posX, posY )
        self.moduleState = SwerveModuleState( 0, Rotation2d(0) )

    def updateOutputs(self):
        """
        Update Network Table Logging
        """
        # Get Logging Table
        tbl = NetworkTableInstance.getDefault().getTable( f"SysOutputs/SwerveDrive/Module{self.name}" )

        # Drive Motor Data
        tbl.putNumber( "drivePositionMeters", self.driveMotorEncoder.getPosition() )
        tbl.putNumber( "driveVelocityMetersPerSec", self.driveMotorEncoder.getVelocity() )
        tbl.putNumber( "driveAppliedVolts", self.driveMotor.getAppliedOutput() * self.driveMotor.getBusVoltage() )
        tbl.putNumber( "driveCurrentAmps", self.driveMotor.getOutputCurrent() )
        tbl.putNumber( "driveTempCelcius", self.driveMotor.getMotorTemperature() )

        # Turn Motor Data
        tbl.putNumber( "turnCanCoder-Relative", units.rotationsToDegrees( self.turnSensor.get_position().value_as_double ) )
        tbl.putNumber( "turnCanCoder-Absolute", units.rotationsToDegrees( self.turnSensor.get_absolute_position().value_as_double ) )
        tbl.putNumber( "turnPositionDegrees", self.turnMotorEncoder.getPosition() )
        tbl.putNumber( "turnVelocityDegreesPerSec", self.turnMotorEncoder.getVelocity() )
        tbl.putNumber( "turnAppliedVolts", self.turnMotor.getAppliedOutput() * self.turnMotor.getBusVoltage() )
        tbl.putNumber( "turnCurrentAmps", self.turnMotor.getOutputCurrent() )
        tbl.putNumber( "turnTempCelcius", self.turnMotor.getMotorTemperature() )

    def updateDriveEncoderConversions(self):
        """
        Update the Onboard Position and Velocity Conversions with the NEO Drive Motor
        """
        driveToMeters = self.driveGearRatio.get() * 2 * math.pi * self.wheelRadius.get()
        self.driveMotorEncoder.setPositionConversionFactor( driveToMeters ) # Meters
        self.driveMotorEncoder.setVelocityConversionFactor( driveToMeters / 60 ) # Meters per Second

    def updateTurnEncoderConversions(self):
        """
        Update the Onboard Position and Velocity Conversions with the NEO Turn Motor
        """
        turnToRadians = self.turnGearRatio.get() * 2 * math.pi
        turnToDegrees = self.turnGearRatio.get() * 360
        self.turnMotorEncoder.setPositionConversionFactor( turnToDegrees ) # Radians
        self.turnMotorEncoder.setVelocityConversionFactor( turnToDegrees / 60 ) # Radians per Second
        self.turnMotorEncoder.setPosition( units.rotationsToDegrees( self.turnSensor.get_position().value_as_double ) )

    def updateDrivePIDController(self):
        """
        Update the PID Controller for the Drive Motor
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

    def updateTurnPIDController(self):
        """
        Update the PID Controller for the Turn Motor
        """
        # Get Slot Index
        slotIdx = self.turn_kSlotIdx.get()

        # Turn Integrated PID Controller
        self.turnMotorPid.setP( self.turn_kP.get(), slotIdx ) # TalonFX.config_kP()
        self.turnMotorPid.setI( self.turn_kI.get(), slotIdx ) # TalonFX.config_kI()
        self.turnMotorPid.setIZone( self.turn_kIZone.get(), slotIdx ) # TalonFX.config_IntegralZone()
        self.turnMotorPid.setD( self.turn_kD.get(), slotIdx ) # TalonFX.config_kD()
        self.turnMotorPid.setFF( self.turn_kF.get(), slotIdx ) # TalonFX.config_kF()

        # Turn Integrated PID - Smart Motion Properties
        self.turnMotorPid.setSmartMotionMaxVelocity( self.turn_mmMaxVelocity.get(), slotIdx ) # TalonFX.configMotionCruiseVelocity()
        self.turnMotorPid.setSmartMotionMaxAccel( self.turn_mmMaxAcceleration.get(), slotIdx ) # TalonFX.configMotionAcceleration
        self.turnMotorPid.setSmartMotionAccelStrategy( SparkMaxPIDController.AccelStrategy.kTrapezoidal, slotIdx ) # TalonFX.configMotionSCurveStrength
        self.turnMotorPid.setSmartMotionAllowedClosedLoopError( self.turn_kError.get(), slotIdx ) #TalonFX.configAllowableClosedloopError()

    def setDriveVelocity(self, velocity:float = 0.0) -> None:
        """
        Set the current drive velocity in meters per second
        """
        # Set Velocity
        velocMode = CANSparkMax.ControlType.kVelocity #if not self.driveSmart.get() else CANSparkMax.ControlType.kSmartVelocity
        self.driveMotorPid.setReference( velocity, velocMode, self.drive_kSlotIdx.get() )

    def setTurnPosition(self, rotation:Rotation2d) -> None:
        """
        Set the current Turning Motor position based on Rotation
        """
        # Set Turn
        turnMode = CANSparkMax.ControlType.kPosition #if not self.turnSmart.get() else CANSparkMax.ControlType.kSmartMotion
        self.turnMotorPid.setReference( rotation.degrees(), turnMode, self.turn_kSlotIdx.get() )

    def getModuleState(self) -> SwerveModuleState:
        """
        Get the Current Module Position in Meters Per Second and Rotation2d

        :returns SwerveModulePosition object
        """
        return SwerveModuleState(
            speed=self.driveMotorEncoder.getVelocity(),
            angle=Rotation2d( self.turnMotorEncoder.getPosition() )
        )


    def getModulePosition(self) -> SwerveModulePosition:
        """
        Get the Current Module Position in Meters Per Second and Rotation2d

        :returns SwerveModulePosition object
        """
        return SwerveModulePosition(
            distance=self.driveMotorEncoder.getPosition(),
            angle=Rotation2d( self.turnMotorEncoder.getPosition() )
        )

