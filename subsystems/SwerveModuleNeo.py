"""
Description: Swerve Module (West Coast Products - Swerve X)
Version:  1
Date:  2023-09-29

Drive Motor Controllers:  TALON/FALCON FX
Angle Motor Controllers:  TALON/FALCON FX
Angle Sensors:  CAN CODERS

Velocity: Closed Loop (FALCON Integrated)
Angle:  Closed Loop (FALCON Integrated)
"""

### Imports
# Python Imports
import math

# FRC Component Imports
from commands2 import SubsystemBase
from ctre import WPI_TalonFX, ControlMode, FeedbackDevice, RemoteFeedbackDevice, NeutralMode, TalonFXPIDSetConfiguration
from ctre.sensors import WPI_CANCoder, SensorInitializationStrategy, AbsoluteSensorRange
from rev import CANSparkMax, SparkMaxPIDController, SparkMaxRelativeEncoder
from wpilib import RobotBase, RobotState
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
from wpimath.geometry import Translation2d, Rotation2d
from wpiutil import *

# Self Made Classes
from .SwerveModule import SwerveModule

### Constants
# Module Physical Constants
driveGearRatio = 1 / 6.75 # ( L1: 8.14:1 | L2: 6.75:1 | L3: 6.12:1 )
wheelRadius = 0.0508 # In Meters
driveToMeters = driveGearRatio * 2 * math.pi * wheelRadius
angleGearRatio = 1 / (150/7) # 150/7:1
angleToRadians = angleGearRatio * 2 * math.pi

# Controller Constants
drive_kP = 0.04
drive_kI = 0.0
drive_kD = 1.0
drive_kF = 0.065
drive_kIZone = 0
drive_kError = 0
drive_kSlotIdx = 0
drive_mmMaxVelocity = 20480
drive_mmMaxAcceleration = 4 * drive_mmMaxVelocity
drive_mmSCurveSmoothing = 8

angle_kP = 0.5
angle_kI = 0
angle_kD = 0
angle_kF = 0
angle_kIZone = 0
angle_kError = 0
angle_kSlotIdx = 0
angle_mmMaxVelocity = 2048
angle_mmMaxAcceleration = 2 * angle_mmMaxVelocity
angle_mmSCurveSmoothing = 8

# Class: SwerveModule
class SwerveModuleNeo(SwerveModule):
    motionMagic:bool = False

    driveMotor:CANSparkMax = None
    angleMotor:CANSparkMax = None
    angleSensor:WPI_CANCoder = None

    referencePosition:Translation2d = None
    moduleState:SwerveModuleState = None

    def __init__(self, subsystemName, driveId, angleId, sensorId, posX, posY, angleOffset):
        ### Module Name
        self.name = subsystemName

        ### Angle Sensor
        self.angleSensor = WPI_CANCoder( sensorId, "canivore1")
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
        self.angleMotorEncoder.setPositionConversionFactor( angleToRadians ) # Radians
        self.angleMotorEncoder.setVelocityConversionFactor( angleToRadians * 60 ) # Radians per Second
        
        self.angleMotorPid = self.angleMotor.getPIDController()
        self.angleMotorPid.setFeedbackDevice( self.angleMotorEncoder ) # WPI_TalonFX.configSelectedFeedbackSensor()  ### Should this be the CAN Coder?
        self.angleMotorPid.setPositionPIDWrappingEnabled( True ) #WPI_TalonFX.configFeedbackNotContinous()
        self.angleMotorPid.setPositionPIDWrappingMinInput( -math.pi )
        self.angleMotorPid.setPositionPIDWrappingMinInput(  math.pi )      

        # Angle Integrated PID Controller
        self.angleMotorPid.setP( angle_kP, angle_kSlotIdx ) # TalonFX.config_kP()
        self.angleMotorPid.setI( angle_kI, angle_kSlotIdx ) # TalonFX.config_kI()
        self.angleMotorPid.setIZone( angle_kIZone, angle_kSlotIdx ) # TalonFX.config_IntegralZone()
        self.angleMotorPid.setD( angle_kD, angle_kSlotIdx ) # TalonFX.config_kD()
        self.angleMotorPid.setFF( angle_kF, angle_kSlotIdx ) # TalonFX.config_kF()

        # Angle Integrated PID - Smart Motion Properties
        self.angleMotorPid.setSmartMotionMaxVelocity( angle_mmMaxVelocity, angle_kSlotIdx ) # TalonFX.configMotionCruiseVelocity()
        self.angleMotorPid.setSmartMotionMaxAccel( angle_mmMaxAcceleration, angle_kSlotIdx ) # TalonFX.configMotionAcceleration
        self.angleMotorPid.setSmartMotionAccelStrategy( SparkMaxPIDController.AccelStrategy.kTrapezoidal, angle_kSlotIdx ) # TalonFX.configMotionSCurveStrength
        self.angleMotorPid.setSmartMotionAllowedClosedLoopError( angle_kError, angle_kSlotIdx ) #TalonFX.configAllowableClosedloopError()

        # Save Angle Motor Config
        self.angleMotor.burnFlash()

        ### Drive Motor
        self.driveMotor = CANSparkMax( driveId, CANSparkMax.MotorType.kBrushless )
        self.driveMotor.restoreFactoryDefaults()
        self.driveMotor.setInverted( True )
        self.driveMotor.setIdleMode( CANSparkMax.IdleMode.kCoast )
        
        self.driveMotorEncoder = self.driveMotor.getEncoder()
        #self.driveMotorEncoder.setInverted(False)
        self.driveMotorEncoder.setPositionConversionFactor( driveToMeters ) # Meters
        self.driveMotorEncoder.setVelocityConversionFactor( driveToMeters * 60 ) # Meters per Second

        self.driveMotorPid = self.driveMotor.getPIDController()
        self.driveMotorPid.setFeedbackDevice( self.driveMotorEncoder ) # WPI_TalonFX.configSelectedFeedbackSensor()    

        # Drive Integrated PID Controller
        self.driveMotorPid.setP( drive_kP, drive_kSlotIdx ) # TalonFX.config_kP()
        self.driveMotorPid.setI( drive_kI, drive_kSlotIdx ) # TalonFX.config_kI()
        self.driveMotorPid.setIZone( drive_kIZone, drive_kSlotIdx ) # TalonFX.config_IntegralZone()
        self.driveMotorPid.setD( drive_kD, drive_kSlotIdx ) # TalonFX.config_kD()
        self.driveMotorPid.setFF( drive_kF, drive_kSlotIdx ) # TalonFX.config_kF()

        # Drive Integrated PID - Motion Magic Properties
        self.driveMotorPid.setSmartMotionMaxVelocity( drive_mmMaxVelocity, drive_kSlotIdx ) # TalonFX.configMotionCruiseVelocity()
        self.driveMotorPid.setSmartMotionMaxAccel( drive_mmMaxAcceleration, drive_kSlotIdx ) # TalonFX.configMotionAcceleration
        self.driveMotorPid.setSmartMotionAccelStrategy( SparkMaxPIDController.AccelStrategy.kTrapezoidal, drive_kSlotIdx ) # TalonFX.configMotionSCurveStrength
        self.driveMotorPid.setSmartMotionAllowedClosedLoopError( drive_kError, drive_kSlotIdx ) #TalonFX.configAllowableClosedloopError()

        ### Swerve Module Information
        self.referencePosition = Translation2d( posX, posY )
        self.moduleState = SwerveModuleState( 0, Rotation2d(0) )

    def setDesiredState(self, desiredState:SwerveModuleState):
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
        velocity *= ( optimalState.angle - currentAngleRotation ).cos() # Scale Speed / Smooth rotation ??? Smart Motion?

        # Set Velocity
        if self.motionMagic:
            self.driveMotorPid.setReference( velocity, CANSparkMax.ControlType.kSmartVelocity, drive_kSlotIdx )
        else:
            self.driveMotorPid.setReference( velocity, CANSparkMax.ControlType.kVelocity, drive_kSlotIdx )

        # Set Angle
        if self.motionMagic:
            self.angleMotorPid.setReference( optimalState.angle.radians(), CANSparkMax.ControlType.kSmartMotion, angle_kSlotIdx )
        else:
            self.angleMotorPid.setReference( optimalState.angle.radians(), CANSparkMax.ControlType.kPosition, angle_kSlotIdx )

    def getReferencePosition(self) -> Translation2d:
        return self.referencePosition
       
    def getModuleState(self) -> SwerveModuleState:
        return self.moduleState

    def getModulePosition(self) -> SwerveModulePosition:
        return SwerveModulePosition(
            distance=self.driveMotorEncoder.getPosition(),
            angle=Rotation2d( self.angleMotorEncoder.getPosition() )
        )
    
    def setMotionMagic(self, state:bool):
        self.motionMagic = state

