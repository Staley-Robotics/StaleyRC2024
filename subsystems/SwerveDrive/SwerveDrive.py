"""
Description: 4 Wheel Swerve Drive Chassis
Version:  1
Date:  2024-01-09

Dependencies:
- SwerveModule:  SwerveModule
- Gyro:          Gyro
"""

### Imports
# Python Imports
import typing
import math

# FRC Component Imports
from commands2 import Subsystem
from wpilib import SmartDashboard, Timer, DriverStation, RobotBase, Field2d
from wpimath.controller import PIDController, ProfiledPIDControllerRadians, HolonomicDriveController
from wpimath.estimator import SwerveDrive4PoseEstimator
from wpimath.geometry import Translation2d, Rotation2d, Pose2d
from wpimath.kinematics import SwerveDrive4Kinematics, ChassisSpeeds, SwerveModulePosition, SwerveModuleState
from wpimath.trajectory import TrapezoidProfileRadians
from wpimath import units
from ntcore import *

from pathplannerlib.auto import AutoBuilder
from pathplannerlib.config import HolonomicPathFollowerConfig, ReplanningConfig, PIDConstants
from pathplannerlib.controller import PPHolonomicDriveController

# Our Imports
from util import *
from .SwerveModuleIO import SwerveModuleIO
from .GyroIO import GyroIO

class SwerveDrive(Subsystem):
    """
    SwerveDrive Subsystem Class used to operate a 4 Wheel SwerveDrive Chassis
    """
    
    def __init__( self,
                  modules:typing.Tuple[ SwerveModuleIO,
                                        SwerveModuleIO,
                                        SwerveModuleIO,
                                        SwerveModuleIO ],
                  gyro:GyroIO=GyroIO() ):
        """
        Initialization of a SwerveDrive
        """
        # Subsystem Setup
        self.setName( "SwerveDrive" )

        # Robot Name
        self.robotName = "Robot"
        if not RobotBase.isReal(): self.robotName = "SimRobot"

        # Get Tunable Properties
        self.isCharacterizing = NTTunableBoolean( "/Characterize/Enabled", False )
        self.charMOI = NTTunableFloat( "/Characterize/SwerveDrive/moiVolts", 0.0 )
        self.charMaxVelocity = NTTunableFloat( "/Characterize/SwerveDrive/maxVelocity", 0.0 )
        self.charMaxAngularVelocity = NTTunableFloat( "/Characterize/SwerveDrive/maxAngularVelocity", 0.0 )
        self.charSettingsVolts = NTTunableFloat( "/Characterize/SwerveDrive/MySettings/volts", 0.0 )
        self.charSettingsRotation = NTTunableBoolean( "/Characterize/SwerveDrive/MySettings/rotation", False )
        
        self.offline = NTTunableBoolean( "/DisableSubsystem/SwerveDrive", False, persistent=True )
        
        self.maxVelocPhysical = NTTunableFloat( "SwerveDrive/Velocity/Physical", 4.50, persistent=True )
        self.maxVelocDriver = NTTunableFloat( "SwerveDrive/Velocity/Driver", 3.50, persistent=True )
        self.maxVelocCode = NTTunableFloat( "SwerveDrive/Velocity/Code", 4.25, persistent=True )

        self.maxAngVelocPhysical = NTTunableFloat( "SwerveDrive/AngularVelocity/Physical", 2 * math.pi, persistent=True )
        self.maxAngVelocDriver = NTTunableFloat( "SwerveDrive/AngularVelocity/Driver", 2 * math.pi, persistent=True )
        self.maxAngVelocCode = NTTunableFloat( "SwerveDrive/AngularVelocity/Code", 2 * math.pi, persistent=True )

        self.maxVelocity = NTTunableFloat( "SwerveDrive/maxVelocity", 3.70 )
        self.maxAngularVelocity = NTTunableFloat( "SwerveDrive/maxAngularVelocity", 2 * math.pi )

        self.pidX_kP = NTTunableFloat( "SwerveDrive/holonomicDriveController/x/kP", 1, self.updateHolonomicDriveController )
        self.pidX_kI = NTTunableFloat( "SwerveDrive/holonomicDriveController/x/kI", 0, self.updateHolonomicDriveController )
        self.pidX_kD = NTTunableFloat( "SwerveDrive/holonomicDriveController/x/kD", 0, self.updateHolonomicDriveController )
        self.pidY_kP = NTTunableFloat( "SwerveDrive/holonomicDriveController/y/kP", 1, self.updateHolonomicDriveController )
        self.pidY_kI = NTTunableFloat( "SwerveDrive/holonomicDriveController/y/kI", 0, self.updateHolonomicDriveController )
        self.pidY_kD = NTTunableFloat( "SwerveDrive/holonomicDriveController/y/kD", 0, self.updateHolonomicDriveController )
        self.pidT_kP = NTTunableFloat( "SwerveDrive/holonomicDriveController/theta/kP", 1, self.updateHolonomicDriveController )
        self.pidT_kI = NTTunableFloat( "SwerveDrive/holonomicDriveController/theta/kI", 0, self.updateHolonomicDriveController )
        self.pidT_kD = NTTunableFloat( "SwerveDrive/holonomicDriveController/theta/kD", 0, self.updateHolonomicDriveController )
        self.pidH_tDistance = NTTunableFloat( "SwerveDrive/holonomicDriveController/tolerance/distance", 0.0254, self.updateHolonomicDriveController )
        self.pidH_tRotation = NTTunableFloat( "SwerveDrive/holonomicDriveController/tolerance/rotation", 0.008, self.updateHolonomicDriveController )

        # Gyro and Modules
        self.gyro = gyro
        self.modules = modules

        self.gyroInputs = self.gyro.GyroIOInputs()
        self.moduleInputs = []
        for mod in self.modules:
            self.moduleInputs.append( mod.SwerveModuleIOInputs() )

        # Kinematics
        self.kinematics = SwerveDrive4Kinematics(
            self.modules[0].getReferencePosition(),
            self.modules[1].getReferencePosition(),
            self.modules[2].getReferencePosition(),
            self.modules[3].getReferencePosition()
        )

        # Odometry
        self.odometry = SwerveDrive4PoseEstimator(
            self.getKinematics(),
            self.gyro.getRotation2d(),
            self.getModulePositions(),
            Pose2d(Translation2d(0,0), Rotation2d(0))
        )
        self.odometry2 = SwerveDrive4PoseEstimator(
            self.getKinematics(),
            self.gyro.getRotation2d(),
            self.getModulePositions(),
            Pose2d(Translation2d(0,0), Rotation2d(0))
        )
        self.odometryWheelsOnly = SwerveDrive4PoseEstimator(
            self.getKinematics(),
            self.gyro.getRotation2d(),
            self.getModulePositions(),
            Pose2d(Translation2d(0,0), Rotation2d(0))
        )

        # PID Controllers for Drive Motion
        self.hPid:HolonomicDriveController = None
        self.updateHolonomicDriveController()

        # PathPlanner Auto Builder
        modulePositions = [
            self.modules[0].getReferencePosition(),
            self.modules[1].getReferencePosition(),
            self.modules[2].getReferencePosition(),
            self.modules[3].getReferencePosition()
        ]
        radius = 0.0
        for i in range(len(modulePositions)):
            radius = max( radius, modulePositions[i].distance( Translation2d(0,0) ) )

        AutoBuilder.configureHolonomic(
            self.getPose, # Robot pose supplier
            self.resetOdometry, # Method to reset odometry (will be called if your auto has a starting pose)
            self.getChassisSpeeds, # ChassisSpeeds supplier. MUST BE ROBOT RELATIVE
            self.runChassisSpeeds, # Method that will drive the robot given ROBOT RELATIVE ChassisSpeeds
            HolonomicPathFollowerConfig( # HolonomicPathFollowerConfig, this should likely live in your Constants class
                PIDConstants(
                    self.pidX_kP.get(),
                    self.pidX_kI.get(),
                    self.pidX_kD.get()
                ), # Translation PID constants
                PIDConstants(
                    self.pidT_kP.get(),
                    self.pidT_kI.get(),
                    self.pidT_kD.get()
                ), # Rotation PID constants
                self.maxVelocPhysical.get(), # Max module speed, in m/s
                radius, # Drive base radius in meters. Distance from robot center to furthest module.
                ReplanningConfig() # Default path replanning config. See the API for the options here
            ),
            self.shouldFlipPath, # Supplier to control path flipping based on alliance color
            self # Reference to this subsystem to set requirements
        )

        PPHolonomicDriveController.setRotationTargetOverride( self.ppAutoTarget )

        # NT Publishing
        if not NetworkTableInstance.getDefault().hasSchema( "SwerveModuleState" ):        
            self.ntSwerveModuleStatesCurrent = NetworkTableInstance.getDefault().getStructTopic( "/StartSchema/SwerveModuleState", SwerveModuleState ).publish( PubSubOptions() )
            self.ntSwerveModuleStatesCurrent.set( SwerveModuleState() ) 
            self.ntSwerveModuleStatesCurrent.close()
        if not NetworkTableInstance.getDefault().hasSchema( "SwerveModuleInputs" ):        
            self.ntSwerveModuleStatesCurrent = NetworkTableInstance.getDefault().getStructTopic( "/StartSchema/SwerveModuleInputs", SwerveModuleIO.SwerveModuleIOInputs ).publish( PubSubOptions() )
            self.ntSwerveModuleStatesCurrent.set( SwerveModuleIO.SwerveModuleIOInputs() ) 
            self.ntSwerveModuleStatesCurrent.close()

        self.ntGyroInputs = NetworkTableInstance.getDefault().getStructTopic( "/SwerveDrive/Gyro", GyroIO.GyroIOInputs ).publish()
        self.ntModuleInputs = NetworkTableInstance.getDefault().getStructArrayTopic( "/SwerveDrive/Modules", SwerveModuleIO.SwerveModuleIOInputs ).publish()

        self.ntRobotPose2d = NetworkTableInstance.getDefault().getStructTopic( "/Logging/Odometry/Robot", Pose2d ).publish()
        self.ntRobotPose2dNoTime = NetworkTableInstance.getDefault().getStructTopic( "/Logging/Odometry/RobotUpdateNoTime", Pose2d ).publish()
        self.ntRobotPose2dWheels = NetworkTableInstance.getDefault().getStructTopic( "/Logging/Odometry/RobotWheelsOnly", Pose2d ).publish()
        self.ntChassisSpeedsCurrent = NetworkTableInstance.getDefault().getStructTopic( "/Logging/ChassisSpeeds/Robot/Current", ChassisSpeeds ).publish()
        self.ntChassisSpeedsNext = NetworkTableInstance.getDefault().getStructTopic( "/Logging/ChassisSpeeds/Robot/Next", ChassisSpeeds ).publish()
        self.ntChassisSpeedsFieldCurrent = NetworkTableInstance.getDefault().getStructTopic( "/Logging/ChassisSpeeds/Field/Current", ChassisSpeeds ).publish()
        self.ntChassisSpeedsFieldNext = NetworkTableInstance.getDefault().getStructTopic( "/Logging/ChassisSpeeds/Field/Next", ChassisSpeeds ).publish()
        self.ntSwerveModuleStatesCurrent = NetworkTableInstance.getDefault().getStructArrayTopic( "/Logging/SwerveModuleStates/Current", SwerveModuleState ).publish( PubSubOptions() )
        self.ntSwerveModuleStatesNext = NetworkTableInstance.getDefault().getStructArrayTopic( "/Logging/SwerveModuleStates/Next", SwerveModuleState ).publish()

    def periodic(self):
        """
        SwerveDrive Periodic Loop
        """
        # Logging
        self.gyro.updateInputs( self.gyroInputs )
        for x in range(len(self.modules)):
            self.modules[x].updateInputs( self.moduleInputs[x] )
        
        self.ntGyroInputs.set( self.gyroInputs )
        self.ntModuleInputs.set( self.moduleInputs )

        # Run Modules
        if DriverStation.isDisabled() or self.offline.get():
            self.stop()

        if self.isCharacterizing.get():
            for module in self.modules:
                module.runCharacterization( self.charSettingsVolts.get(), self.charSettingsRotation.get() )
        else:
            for module in self.modules:
                module.run()

        # Odometry from Module Position Data
        pose = self.odometry.updateWithTime(
            Timer.getFPGATimestamp(),
            self.gyro.getRotation2d(),
            self.getModulePositions()
        )
        pose2 = self.odometry2.update(
            self.gyro.getRotation2d(),
            self.getModulePositions()
        )
        pose3 = self.odometryWheelsOnly.update(
            self.gyro.getRotation2d(),
            self.getModulePositions()
        )

        # Logging: RobotPose, ChassisSpeeds, SwerveModuleStates Speeds
        self.ntRobotPose2d.set( pose )
        self.ntRobotPose2dNoTime.set( pose2 )
        self.ntRobotPose2dWheels.set( pose3 )
        self.ntChassisSpeedsCurrent.set( self.getChassisSpeeds() )
        self.ntChassisSpeedsFieldCurrent.set( self.getChassisSpeeds(True) )
        self.ntSwerveModuleStatesCurrent.set( self.getModuleStates() )
        self.ntChassisSpeedsNext.set( self.getChassisSpeedsSetpoint() )
        self.ntChassisSpeedsFieldNext.set( self.getChassisSpeedsSetpoint(True) )
        self.ntSwerveModuleStatesNext.set( self.getModuleSetpoints() )

    def simulationPeriodic(self) -> None:
        """
        SwerveDrive Simulation Periodic Loop
        """
        self.gyro.simulationPeriodic( self.getRotationVelocity() )

    def shouldFlipPath(self):
        """
        Should Path Planning Be Flipped
        """
        return DriverStation.getAlliance() == DriverStation.Alliance.kRed

    def ppAutoTarget(self):
        target = -1
        # target = -1 -> None
        # target = 0 -> Speaker
        # target = 1 -> Amp
        # target = 2 -> Source
        # target = 3 -> Stage Left
        # target = 4 -> Stage Center
        # target = 5 -> Stage Right
        return None

    def syncGyro(self) -> None:
        print( f"Old Gyro: {self.gyro.getRotation2d().degrees()} Pose: {self.getPose().rotation().degrees() }")
        pose = self.getPose()
        self.gyro.setYaw( pose.rotation().degrees() )
        self.getOdometry(0).resetPosition(
            self.gyro.getRotation2d(),
            self.getModulePositions(),
            pose
        )
        self.getOdometry(1).resetPosition(
            self.gyro.getRotation2d(),
            self.getModulePositions(),
            pose
        )
        self.getOdometry(2).resetPosition(
            self.gyro.getRotation2d(),
            self.getModulePositions(),
            self.getOdometry(2).getEstimatedPosition()
        )
        print( f"New Gyro: {self.gyro.getRotation2d().degrees()} Pose: {self.getPose().rotation().degrees() }")

    def resetOdometry(self, pose:Pose2d = Pose2d( Translation2d(0, 0), Rotation2d(0) ) ) -> None:
        self.gyro.setYaw( pose.rotation().degrees() )
        self.odometry.resetPosition(
            self.gyro.getRotation2d(),
            self.getModulePositions(),
            pose
        )
        pass

    def getKinematics(self) -> SwerveDrive4Kinematics:
        """
        Get the Kinematics configuration of this SwerveDrive

        :returns: SwerveDrive4Kinematics
        """
        return self.kinematics
       
    def getOdometry(self, version = 0) -> SwerveDrive4PoseEstimator:
        """
        Get The Current Odometry (fused with Vision Data) of this SwerveDrive

        :returns: SwerveDrive4PoseEstimator
        """
        match version:
            case 0:
                return self.odometry
            case 1:
                return self.odometry2
            case 2:
                return self.odometryWheelsOnly
        return self.odometry

    def updateHolonomicDriveController(self) -> None:
        """
        Update the HolonomicDriveController configuration for this SwerveDrive

        :returns: HolonomicDriveController
        """
        x = PIDController(
            self.pidX_kP.get(),
            self.pidX_kI.get(),
            self.pidX_kD.get()
        )
        y = PIDController(
            self.pidY_kP.get(),
            self.pidY_kI.get(),
            self.pidY_kD.get()
        )
        theta = ProfiledPIDControllerRadians(
            self.pidT_kP.get(),
            self.pidT_kI.get(),
            self.pidT_kD.get(),
            TrapezoidProfileRadians.Constraints(
                self.maxAngularVelocity.get(),
                self.maxAngularVelocity.get() * 2
            )
        )
        theta.enableContinuousInput( -math.pi, math.pi )
        theta.reset( self.getRobotAngle().radians(), self.getRotationVelocity() )

        self.hPid = HolonomicDriveController( x, y, theta )
        self.hPid.setTolerance(
            Pose2d(
                Translation2d( 
                    self.pidH_tDistance.get(),
                    self.pidH_tDistance.get()
                ),
                Rotation2d( self.pidH_tRotation.get() )
            )
        )

        self.resetHolonomicDriveController()

    def resetHolonomicDriveController(self) -> None:
        """
        Reset the HolonomicDriveController for this SwerveDrive
        """
        self.hPid.getXController().reset()
        self.hPid.getYController().reset()
        self.hPid.getThetaController().reset(
            self.getRobotAngle().radians(),
            self.getRotationVelocity()
        )

    def getHolonomicDriveController(self) -> HolonomicDriveController:
        """
        Get the HolonomicDriveController for this SwerveDrive

        :returns: HolonomicDriveController
        """
        #self.resetHolonomicDriveController()
        return self.hPid

    def getPose(self) -> Pose2d:
        """
        Get the Current Pose from the Odometry data of this SwerveDrive
        
        :returns: Pose2d
        """
        return self.getOdometry().getEstimatedPosition()
    
    def getRobotAngle(self) -> Rotation2d:
        """
        Get the Current Rotation based on the gyroscope of this SwerveDrive 

        :returns: Rotation2d
        """
        return self.gyro.getRotation2d()

    def getRotationVelocity(self, fieldRelative:bool = False) -> float:
        """
        Get the Angular Velocity of this SwerveDrive
        
        :returns: float in radians per second
        """
        return self.getChassisSpeeds(fieldRelative).omega
    
    def getRotationVelocitySetpoint(self, fieldRelative:bool = False) -> float:
        """
        Get the Angular Velocity of this SwerveDrive's Future Setpoint
        
        :returns: float in radians per second
        """
        return self.getChassisSpeedsSetpoint(fieldRelative).omega

    def getChassisSpeeds(self, fieldRelative:bool = False) -> ChassisSpeeds:
        """
        Get the Current Chassis Speeds based on the Wheel Measurements
        
        :returns: ChassisSpeeds in meters per second velocity in x and y direction and rotations per
        """
        cSpeeds = self.getKinematics().toChassisSpeeds( self.getModuleStates() )
        if fieldRelative: cSpeeds = ChassisSpeeds.fromRobotRelativeSpeeds( cSpeeds, self.getRobotAngle() )
        return cSpeeds
    
    def getChassisSpeedsSetpoint(self, fieldRelative:bool = False) -> ChassisSpeeds:
        """
        Get the Chassis Speeds based on the Wheel Measurements
        
        :returns: ChassisSpeeds in meters per second velocity in x and y direction and rotations per
        """
        cSpeeds = self.getKinematics().toChassisSpeeds( self.getModuleSetpoints() )
        if fieldRelative: cSpeeds = ChassisSpeeds.fromRobotRelativeSpeeds( cSpeeds, self.getRobotAngle() )
        return cSpeeds

    def getModuleSetpoints(self) -> typing.Tuple[ SwerveModuleState,
                                               SwerveModuleState,
                                               SwerveModuleState,
                                               SwerveModuleState ]:
        """
        Returns all of the SwerveModuleStates of the SwerveModules on this SwerveDrive

        :returns: Tuple of SwerveModuleStates (velocity, rotation)
        """
        return tuple( modules.getModuleSetpoint() for modules in self.modules )

    def getModuleStates(self) -> typing.Tuple[ SwerveModuleState,
                                               SwerveModuleState,
                                               SwerveModuleState,
                                               SwerveModuleState ]:
        """
        Returns all of the SwerveModuleStates of the SwerveModules on this SwerveDrive

        :returns: Tuple of SwerveModuleStates (velocity, rotation)
        """
        return tuple( modules.getModuleState() for modules in self.modules )

    def getModulePositions(self) -> typing.Tuple[ SwerveModulePosition,
                                                  SwerveModulePosition,
                                                  SwerveModulePosition,
                                                  SwerveModulePosition ]:
        """
        Returns all of the SwerveModulePositions of the SwerveModules on this SwerveDrive

        :returns: Tuple of SwerveModulePosition (distance, rotation)
        """
        return tuple( modules.getModulePosition() for modules in self.modules )

    """
    Characterization Functions
    """
    def runCharacterization(self, volts:float = 0.0, rotation:bool = False) -> None:
        """
        :param volts: volts to run drive motors at
        :param rotation: state of rotation
        """
        self.charSettingsVolts.set(volts)
        self.charSettingsRotation.set(rotation)

    def getVelocityConfig(self) -> [float,float]:
        return [ self.maxVelocCode.get(), self.maxAngVelocCode.get() ]

    """
    DriveTime Functions
    """
    def stop(self): # -> CommandBase:
        """
        Stops this SwerveDrive
        """
        self.runChassisSpeeds( ChassisSpeeds(0,0,0) )

    def runPercentageInputs(self, x:float = 0.0, y:float = 0.0, r:float = 0.0) -> None:
        """
        Runs this SwerveDrive in x,y velocities and r rotations based on the maximum velocity characterized
        """
        x = min( max( x, -1.0 ), 1.0 )
        y = min( max( y, -1.0 ), 1.0 )
        r = min( max( r, -1.0 ), 1.0 )

        veloc_x = x * self.maxVelocDriver.get()
        veloc_y = y * self.maxVelocDriver.get()
        veloc_r = r * self.maxAngVelocDriver.get()

        if self.isFieldRelative():
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

        # Send ChassisSpeeds
        self.runChassisSpeeds(speeds)

    def runChassisSpeeds(self, speeds:ChassisSpeeds, convertToFieldRelative:bool = False) -> None:
        """
        Runs this SwerveDrive based on the provided ChassisSpeed
        """
        if convertToFieldRelative: speeds = ChassisSpeeds.fromRobotRelativeSpeeds( speeds, self.getRobotAngle() ) # Needed for Trajectory State not being field relative
        modStates = self.getKinematics().toSwerveModuleStates(speeds, Translation2d(0, 0)) # Convert to SwerveModuleState
        self.runSwerveModuleStates( modStates )

    def runSwerveModuleStates(self, states:typing.Tuple[ SwerveModuleState,
                                                         SwerveModuleState,
                                                         SwerveModuleState,
                                                         SwerveModuleState ]) -> None:
        """
        Runs this SwerveDrive based on provided SwerveModuleState.

        This method will optomize the SwerveModuleState prior to use to minimize the turning to less than 90 degrees
        """
        # Update Desired State for each Swerve Module
        optStates = SwerveDrive4Kinematics.desaturateWheelSpeeds(states, self.maxVelocPhysical.get())
        for x in range(len(self.modules)):
            optimalState:SwerveModuleState = SwerveModuleState.optimize(
                optStates[x],
                self.modules[x].getModulePosition().angle
            )
            self.modules[x].setModuleState( optimalState )
