"""
Description: 4 Wheel Swerve Drive Chassis
Version:  1
Date:  2024-01-03

Dependencies:
- SwerveModule:  SwerveModuleNeo

CAN Network:  CANIVORE
Gyroscope:  PIGEON v2
"""

### Imports
# Python Imports
import typing
import math

# FRC Component Imports
from ctre.sensors import WPI_Pigeon2
from wpilib import SmartDashboard, Timer, DriverStation, RobotBase, Field2d
from wpimath.controller import HolonomicDriveController, PIDController, ProfiledPIDControllerRadians
from wpimath.geometry import Translation2d, Rotation2d, Pose2d
from wpimath.kinematics import SwerveDrive4Kinematics, ChassisSpeeds, SwerveModuleState
from wpimath.estimator import SwerveDrive4PoseEstimator
from wpimath.filter import SlewRateLimiter
from wpimath.trajectory import TrapezoidProfileRadians
from ntcore import *

# Our Imports
from util import *
from .SwerveDrive import SwerveDrive
from .SwerveModuleNeo import SwerveModuleNeo

### Constants
# SwerveDrive Module Input Deadband
gyroStartHeading = NTTunableFloat( "SwerveDrive/gyroStartHeading", -180.0 )

# SwerveDrive Maximum Speeds
maxVelocity = NTTunableFloat( "SwerveDrive/maxVelocity", 3.70 )
maxAngularVelocity = NTTunableFloat( "SwerveDrive/maxAngularVelocity", 2 * math.pi )

# Trajectory Maximums
kMaxSpeedMetersPerSecond = 3
kMaxAccelMetersPerSecondSq = 3
kMaxAngularSpeedMetersPerSecond = NTTunableFloat( "SwerveDrive/kMaxAngularSpeed", 2 * math.pi )  # Code Based Rotation Maximum
kMaxAngularAccelMetersPerSecondSq = NTTunableFloat( "SwerveDrive/kMaxAngularAccel", 4 * math.pi )

### Class: SwerveDrive
class SwerveDriveNeo(SwerveDrive):
    __ntTbl__ = NetworkTableInstance.getDefault().getTable("SwerveDrive")
    fieldRelative:SwerveDrive.BooleanProperty = SwerveDrive.BooleanProperty("fieldRelative", True)
    halfSpeed:SwerveDrive.BooleanProperty = SwerveDrive.BooleanProperty("halfSpeed", False)
    motionMagic:SwerveDrive.BooleanProperty = SwerveDrive.BooleanProperty("motionMagic", False)
    holonomicPID:HolonomicDriveController = None

    # Initialization
    def __init__(self):
        # Subsystem Setup
        super().__init__()
        self.setSubsystem( "SwerveDrive" )
        self.setName( "SwerveDrive" )

        # Robot Name
        self.robotName = "Robot"
        if not RobotBase.isReal(): self.robotName = "SimRobot"

        # Gyro
        self.gyro = WPI_Pigeon2( 61, "rio" )
        self.gyro.reset()
        self.gyro.setYaw( gyroStartHeading.get() )
        if RobotBase.isSimulation(): self.gyro.getSimCollection().setRawHeading( gyroStartHeading.get() )

        # Swerve Modules
        self.moduleFL = SwerveModuleNeo("FrontLeft",  7, 8, 18,  0.25,  0.25,   31.289 ) #211.289)
        self.moduleFR = SwerveModuleNeo("FrontRight", 5, 6, 16,  0.25, -0.25,  -54.932 ) #125.068) #  35.684)
        self.moduleBL = SwerveModuleNeo("BackLeft",   3, 4, 14, -0.25,  0.25,   43.945 ) #223.945)
        self.moduleBR = SwerveModuleNeo("BackRight",  1, 2, 12, -0.25, -0.25, -114.346 )  #65.654)

        # Subsystem Dashboards
        self.addChild( "Gyro", self.gyro )
        #self.addChild( "FrontLeft", self.moduleFL )
        #self.addChild( "FrontRight", self.moduleFR )
        #self.addChild( "BackLeft", self.moduleBL )
        #self.addChild( "BackRight", self.moduleBR )

        # Kinematics
        self.kinematics = SwerveDrive4Kinematics(
            self.moduleFL.getReferencePosition(),
            self.moduleFR.getReferencePosition(),
            self.moduleBL.getReferencePosition(),
            self.moduleBR.getReferencePosition()
        )

        # Odometry
        self.odometry = SwerveDrive4PoseEstimator(
            self.kinematics,
            self.gyro.getRotation2d(),
            [
                self.moduleFL.getModulePosition(),
                self.moduleFR.getModulePosition(),
                self.moduleBL.getModulePosition(),
                self.moduleBR.getModulePosition()
            ],
            Pose2d(Translation2d(2.10,4.0), Rotation2d().fromDegrees(gyroStartHeading.get()))
        )

        # Holonomic PID
        xPid = PIDController( 1.0, 0, 0 )
        xPid.setTolerance( 0.05 )
        xPid.reset()

        yPid = PIDController( 1.0, 0, 0 )
        yPid.setTolerance( 0.05 )
        yPid.reset()

        tPidConstraints = TrapezoidProfileRadians.Constraints(
            kMaxAngularSpeedMetersPerSecond.get(),
            kMaxAngularAccelMetersPerSecondSq.get()
        )
        tPid = ProfiledPIDControllerRadians( 1, 0, 0, tPidConstraints )
        tPid.enableContinuousInput( -math.pi, math.pi )
        tPid.setTolerance( 0.00872 ) #436 )
        tPid.reset( self.getRobotAngle().radians() )

        self.holonomicPID = HolonomicDriveController(
            xPid,
            yPid,
            tPid
        )
        
        self.srl_vx = SlewRateLimiter( 12 )
        self.srl_vy = SlewRateLimiter( 12 )
        self.srl_vr = SlewRateLimiter( 12 )

        # Field on Shuffleboard
        SmartDashboard.putData("Field", Field2d())

    # Update Odometry Information on each loop
    def periodic(self):
        # Odometry from Module Position Data
        pose = self.odometry.updateWithTime(
            Timer.getFPGATimestamp(),
            self.gyro.getRotation2d(),
            [
                self.moduleFL.getModulePosition(),
                self.moduleFR.getModulePosition(),
                self.moduleBL.getModulePosition(),
                self.moduleBR.getModulePosition()
            ]
        )
        
        # Update Data on Dashboard
        poseX = round( pose.X(), 3 )
        poseY = round( pose.Y(), 3 )
        poseR = round( pose.rotation().degrees(), 3 )
        
        self.__ntTbl__.putNumber( "PositionX", poseX )
        self.__ntTbl__.putNumber( "PositionY", poseY )
        self.__ntTbl__.putNumber( "Rotation", poseR )

        if DriverStation.getAlliance() == DriverStation.Alliance.kRed:
            poseX = 16.523 - poseX
            poseY = 8.013 - poseY
            poseR = poseR - 180
 
        SmartDashboard.putData(
            "Field/{self.robotName}",
            Pose2d( poseX, poseY, poseR )
        )

    def simulationPeriodic(self) -> None:
        pass

    ### Drive Based Functions
    # Stop Drivetrain
    def stop(self): # -> CommandBase:
        self.runChassisSpeeds( ChassisSpeeds(0,0,0) )



    # Returns Halfspeed Mode Status
    def isHalfspeed(self):
        return self.halfSpeed.get()

    # Returns Field Relative Status
    def isFieldRelative(self):
        return self.fieldRelative.get()

    # Enable / Disable Motion Magic
    def setMotionMagic(self) -> None:
        mmValue = self.motionMagic.get()
        self.moduleFL.setMotionMagic( mmValue )
        self.moduleFR.setMotionMagic( mmValue )
        self.moduleBL.setMotionMagic( mmValue )
        self.moduleBR.setMotionMagic( mmValue )



    #### Get 
    # PID Controller
    def getHolonomicPIDController(self) -> HolonomicDriveController:
        return self.holonomicPID

    # Kinematics
    def getKinematics(self) -> SwerveDrive4Kinematics:
        return self.kinematics
       
    # Get Odometry Object
    def getOdometry(self) -> SwerveDrive4PoseEstimator:
        return self.odometry

    # Get Pose
    def getPose(self) -> Pose2d:
        return self.odometry.getEstimatedPosition()
    
    # Get Heading of Rotation
    def getRobotAngle(self) -> Rotation2d:
        return self.gyro.getRotation2d()

    # Get ChassisSpeeds
    def getChassisSpeeds(self) -> ChassisSpeeds:
        return self.kinematics.toChassisSpeeds(
            self.moduleFL.getModuleState(),
            self.moduleFR.getModuleState(),
            self.moduleBL.getModuleState(),
            self.moduleBR.getModuleState()
        )
    



    
    ### Run SwerveDrive Functions
    def runPercentageInputs(self, x:float = 0.0, y:float = 0.0, r:float = 0.0) -> None:
        veloc_x = x * maxVelocity.get()
        veloc_y = y * maxVelocity.get()
        veloc_r = r * maxAngularVelocity.get()

        veloc_x = self.srl_vx.calculate( veloc_x )
        veloc_y = self.srl_vy.calculate( veloc_y )
        veloc_r = self.srl_vr.calculate( veloc_r )

        if self.fieldRelative.get():
            speeds = ChassisSpeeds.fromFieldRelativeSpeeds(
                vx = veloc_x,
                vy = veloc_y,
                omega = veloc_r, # radians per second
                robotAngle = self.getRobotAngle()
            )
        else:
            speeds = ChassisSpeeds(
                vx = veloc_x,
                vy = veloc_y,
                omega = veloc_r
            )

        self.holonomicPID.getThetaController().reset(
            self.gyro.getRotation2d().radians(),
            veloc_r
        )

        # Send ChassisSpeeds
        self.runChassisSpeeds(speeds)

    # Run SwerveDrive using ChassisSpeeds
    def runChassisSpeeds(self, speeds:ChassisSpeeds, convertFieldRelative:bool = False) -> None:
        if convertFieldRelative: speeds = ChassisSpeeds.fromFieldRelativeSpeeds( speeds, self.getRobotAngle() ) # Needed for Trajectory State not being field relative
        rotationCenter = Translation2d(0, 0)
        modStates = self.kinematics.toSwerveModuleStates(speeds, rotationCenter) # Convert to SwerveModuleState
        self.runSwerveModuleStates(list(modStates))

    # Run SwerveDrive using SwerveModuleStates
    def runSwerveModuleStates(self, states:typing.List[SwerveModuleState]) -> None:
        # Update Desired State for each Swerve Module
        modStates = SwerveDrive4Kinematics.desaturateWheelSpeeds(states, maxVelocity.get())
        self.moduleFL.setDesiredState(modStates[0])
        self.moduleFR.setDesiredState(modStates[1])
        self.moduleBL.setDesiredState(modStates[2])
        self.moduleBR.setDesiredState(modStates[3])


