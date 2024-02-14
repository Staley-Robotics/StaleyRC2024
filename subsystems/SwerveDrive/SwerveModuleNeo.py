"""
Description: Swerve Module (West Coast Products - Swerve X)
Version:  1
Date:  2024-01-09

Drive Motor Controllers:  REV NEO 
Turn Motor Controllers:  REV NEO
Turn Sensors:  CAN CODERS

Velocity: Closed Loop (SparkMAX Integrated)
Turn:  Closed Loop (SparkMAX Integrated)
"""

### Imports
# Python Imports
import math

# FRC Component Imports
from phoenix5.sensors import WPI_CANCoder, SensorInitializationStrategy, AbsoluteSensorRange
from rev import * #CANSparkMax, SparkMaxPIDController, SparkMaxAlternateEncoder, SparkMaxAbsoluteEncoder, AbsoluteEncoder, RelativeEncoder
from ntcore import NetworkTableInstance
from wpilib import RobotBase
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
from wpimath.geometry import Translation2d, Rotation2d
from wpimath import units

# Self Made Classes
from .SwerveModule import SwerveModule
from util import *

# Class: SwerveModule
class SwerveModuleNeo(SwerveModule):
    """
    Custom SwerveModuleNeo using NEO drive and turn motors on a live robot.

    CTRE CANCoders are used for Absolute position on the turn motor.
    """

    driveMotor:CANSparkMax = None
    turnMotor:CANSparkMax = None
    turnSensor:WPI_CANCoder = None

    referencePosition:Translation2d = None
    moduleState:SwerveModuleState = None

    def __init__(self, subsystemName, driveId, turnId, sensorId, posX, posY, turnOffset):
        """
        Initialization
        """
        ### Module Name
        super().__init__()
        self.name = subsystemName

        ### Tunable Variables
        # Physical Neo Specific Drive Motor PID Values
        self.driveSmart = NTTunableBoolean( "SwerveModule/Drive/smartMotion", False )
        self.drive_kSlotIdx = NTTunableInt( "SwerveModule/Drive/PID/kSlotIdx", 0, self.updateDrivePIDController )
        self.drive_mmMaxVelocity = NTTunableInt( "SwerveModule/Drive/PID/smartVelocity", 20480, self.updateDrivePIDController )
        self.drive_mmMaxAcceleration = NTTunableInt( "SwerveModule/Drive/PID/smartAccel", 4 * self.drive_mmMaxVelocity.get(), self.updateDrivePIDController )

        # Turn Motor PID Values
        self.turnSmart = NTTunableBoolean( "SwerveModule/Turn/smartMotion", False )
        self.turn_kSlotIdx = NTTunableInt( "SwerveModule/Turn/PID/kSlotIdx", 0, self.updateTurnPIDController )
        self.turn_mmMaxVelocity = NTTunableInt( "SwerveModule/Turn/PID/smartVelocity", 2048, self.updateTurnPIDController )
        self.turn_mmMaxAcceleration = NTTunableInt( "SwerveModule/Turn/PID/smartAccel", 2 * self.turn_mmMaxVelocity.get(), self.updateTurnPIDController )

        ### Turn Sensor
        self.turnSensor = WPI_CANCoder( sensorId ) #, "canivore1")
        self.turnSensor.configFactoryDefault()
        self.turnSensor.configSensorInitializationStrategy(SensorInitializationStrategy.BootToZero)
        self.turnSensor.configAbsoluteSensorRange(AbsoluteSensorRange.Unsigned_0_to_360)
        self.turnSensor.configSensorDirection(False)
        if not RobotBase.isSimulation(): self.turnSensor.setPosition(self.turnSensor.getAbsolutePosition() - turnOffset)

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
        #self.turnMotorPid.setOutputRange( -0.15, 0.15 )
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
        self.referencePosition = Translation2d( posX, posY )
        self.moduleState = SwerveModuleState( 0, Rotation2d(0) )

    def updateInputs(self, inputs:SwerveModule.SwerveModuleInputs):
        """
        Update SwerveModuleInputs Values for Logging Purposes
        :param inputs: SwerveModuleInputs objects that need to be updated
        """
        # Drive Motor Data
        inputs.driveTempCelcius = self.driveMotor.getMotorTemperature()
        if inputs.driveTempCelcius != 0:
            inputs.driveMtrsPosition = self.driveMotorEncoder.getPosition()
            inputs.driveMtrsPerSecVelocity = self.driveMotorEncoder.getVelocity()
            #inputs.driveRadPosition = inputs.driveMtrsPosition / self.wheelRadius.get()
            #inputs.driveRadPerSecVelocity = inputs.driveMtrsPerSecVelocity / self.wheelRadius.get()
            inputs.driveAppliedVolts = self.driveMotor.getAppliedOutput() * self.driveMotor.getBusVoltage()
        
        # Turn Motor Data
        inputs.turnTempCelcius = self.turnMotor.getMotorTemperature()
        if inputs.turnTempCelcius != 0:
            inputs.turnCanCoderRelative = self.turnSensor.getPosition()
            inputs.turnCanCoderAbsolute = self.turnSensor.getAbsolutePosition()
            inputs.turnDegPosition = self.turnMotorEncoder.getPosition()
            inputs.turnDegPerSecVelocity = self.turnMotorEncoder.getVelocity()
            #inputs.turnRadPosition = units.degreesToRadians( inputs.turnDegPosition )
            #inputs.turnRadPerSecVelocity = units.degreesToRadians( inputs.turnDegPerSecVelocity )
            inputs.turnAppliedVolts = self.turnMotor.getAppliedOutput() * self.turnMotor.getBusVoltage()
            inputs.turnCurrentAmps = self.turnMotor.getOutputCurrent()
            

        self.moduleState = SwerveModuleState(
            speed=inputs.driveMtrsPerSecVelocity,
            angle=Rotation2d(0).fromDegrees( inputs.turnCanCoderRelative )
        )
        self.modulePosition =  SwerveModulePosition(
            distance=inputs.driveMtrsPosition,
            angle=Rotation2d(0).fromDegrees( inputs.turnCanCoderRelative )
        )

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
        self.turnMotorEncoder.setPosition( self.turnSensor.getPosition() )

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

    def setDriveVoltage(self, volts:float = 0.0) -> None:
        """
        Set the current drive motor voltage in volts

        :param volts: motor voltage (range -12.0 -> 12.0)
        """
        self.driveMotor.setVoltage( volts )

    def setDriveVelocity(self, velocity: float = 0) -> None:
        """
        Set the current drive velocity in meters per second

        :param velocity: velocity (meters per second)
        """
        # Set Velocity
        velocMode = CANSparkMax.ControlType.kVelocity #if not self.driveSmart.get() else CANSparkMax.ControlType.kSmartVelocity
        self.driveMotorPid.setReference( velocity, velocMode, self.drive_kSlotIdx.get() )

    def setTurnPosition(self, rotation:Rotation2d = Rotation2d) -> None:
        """
        Set the current Turning Motor position based on Rotation

        :param rotation: rotation (Rotation2d)
        """
        # Set Angle
        turnMode = CANSparkMax.ControlType.kPosition #if not self.turnSmart.get() else CANSparkMax.ControlType.kSmartMotion
        self.turnMotorPid.setReference( rotation.degrees(), turnMode, self.turn_kSlotIdx.get() )