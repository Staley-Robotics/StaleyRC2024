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
from wpimath.geometry import Translation2d, Rotation2d, Pose2d
from wpimath.kinematics import SwerveDrive4Kinematics, ChassisSpeeds, SwerveModulePosition, SwerveModuleState
from wpimath.estimator import SwerveDrive4PoseEstimator
from ntcore import *

# Our Imports
from util import *
from .SwerveModule import SwerveModule
from .Gyro import Gyro

### Class: SwerveDrive
class SwerveDrive(Subsystem):
    """
    SwerveDrive Subsystem Class used to operate a 4 Wheel SwerveDrive Chassis
    """


    __ntTbl__ = NetworkTableInstance.getDefault().getTable("SwerveDrive")

    # Initialization
    def __init__( self,
                  modules:typing.Tuple[ SwerveModule,
                                        SwerveModule,
                                        SwerveModule,
                                        SwerveModule ],
                  gyro:Gyro=Gyro() ):
        """
        Initialization of a SwerveDrive
        """
        # Subsystem Setup
        super().__init__()
        self.setName( "SwerveDrive" )

        # Robot Name
        self.robotName = "Robot"
        if not RobotBase.isReal(): self.robotName = "SimRobot"

        # Get Tunable Properties
        self.isCharacterizing = NTTunableBoolean( "Characterizing/Enabled", False )
        self.characterizationVolts = NTTunableFloat( "Characterizing/SwerveDriveVolts", 0.0 )

        self.fieldRelative = NTTunableBoolean( "SwerveDrive/fieldRelative", True )

        self.maxVelocity = NTTunableFloat( "SwerveDrive/maxVelocity", 3.70 )
        self.maxAngularVelocity = NTTunableFloat( "SwerveDrive/maxAngularVelocity", 2 * math.pi )

        # Logging
        self.__logTbl__ = NetworkTableInstance.getDefault().getTable(f"{self.robotName}/SwerveDrive")

        # Gyro and Modules
        self.modules = modules
        self.gyro = gyro

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
            Pose2d(Translation2d(0,0), Rotation2d())
        )

        # Field on Shuffleboard
        self.field = Field2d()
        SmartDashboard.putData("Field", self.field)

        # NT Publishing
        self.ntRobotPose2d = NetworkTableInstance.getDefault().getStructTopic( "/Logging/Odometry/Robot", Pose2d ).publish()
        self.ntChassisSpeedsCurrent = NetworkTableInstance.getDefault().getStructTopic( "/Logging/ChassisSpeeds/Current", ChassisSpeeds ).publish()
        self.ntChassisSpeedsNext = NetworkTableInstance.getDefault().getStructTopic( "/Logging/ChassisSpeeds/Next", ChassisSpeeds ).publish()

        if not NetworkTableInstance.getDefault().hasSchema( "SwerveModuleState"):        
            self.ntSwerveModuleStatesCurrent = NetworkTableInstance.getDefault().getStructTopic( "/StartSchema/SwerveModuleState", SwerveModuleState ).publish( PubSubOptions() )
            self.ntSwerveModuleStatesCurrent.set( SwerveModuleState() ) 
            self.ntSwerveModuleStatesCurrent.close()

        self.ntSwerveModuleStatesCurrent = NetworkTableInstance.getDefault().getStructArrayTopic( "/Logging/SwerveModuleStates/Current", SwerveModuleState ).publish( PubSubOptions() )
        self.ntSwerveModuleStatesNext = NetworkTableInstance.getDefault().getStructArrayTopic( "/Logging/SwerveModuleStates/Next", SwerveModuleState ).publish()
        self.ntSwerveModuleStatesNextOptimized = NetworkTableInstance.getDefault().getStructArrayTopic( "/Logging/SwerveModuleStates/NextOptimized", SwerveModuleState ).publish()

    # Update Odometry Information on each loop
    def periodic(self):
        """
        SwerveDrive Periodic Loop
        """
        # Logging
        self.gyro.updateOutputs()
        for module in self.modules:
            module.updateOutputs()

        # Run Modules
        if DriverStation.isDisabled():
            self.stop()
        elif self.isCharacterizing.get():
            #for module in self.modules:
            #    module.driveMotor.set( self.characterizationVolts.get() )
            pass
        else:
            pass

        
        # Odometry from Module Position Data
        pose = self.getOdometry().updateWithTime(
            Timer.getFPGATimestamp(),
            self.gyro.getRotation2d(),
            self.getModulePositions()
        )

        # Logging Current Chassis Speeds
        self.ntChassisSpeedsCurrent.set( self.getChassisSpeeds() )
        self.ntSwerveModuleStatesCurrent.set( self.getModuleStates() )
        self.ntRobotPose2d.set( pose )
        
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
 
        # self.field.setRobotPose(
        #     Pose2d(
        #         Translation2d( poseX, poseY),
        #         Rotation2d().fromDegrees(poseR)
        #     )
        # )
        SmartDashboard.putNumberArray(
            f"Field/{self.robotName}",
            [ poseX, poseY, poseR ]
        )

    def simulationPeriodic(self) -> None:
        """
        SwerveDrive Simulation Periodic Loop
        """
        pass

    ### Drive Based Functions
    # Returns Field Relative Status
    def isFieldRelative(self) -> bool:
        """
        Get the Field Relative Drive State of this SwerveDrive

        :returns: boolean
        """
        return self.fieldRelative.get()

    # Kinematics
    def getKinematics(self) -> SwerveDrive4Kinematics:
        """
        Get the Kinematics configuration of this SwerveDrive

        :returns: SwerveDrive4Kinematics
        """
        return self.kinematics
       
    # Get Odometry Object
    def getOdometry(self) -> SwerveDrive4PoseEstimator:
        """
        Get The Current Odometry (fused with Vision Data) of this SwerveDrive

        :returns: SwerveDrive4PoseEstimator
        """
        return self.odometry

    # Get Pose
    def getPose(self) -> Pose2d:
        """
        Get the Current Pose from the Odometry data of this SwerveDrive
        
        :returns: Pose2d
        """
        return self.getOdometry().getEstimatedPosition()
    
    # Get Heading of Rotation
    def getRobotAngle(self) -> Rotation2d:
        """
        Get the Current Rotation based on the gyroscope of this SwerveDrive 

        :returns: Rotation2d
        """
        return self.gyro.getRotation2d()

    # Get Angular Velocity
    def getRotationVelocity(self) -> float:
        """
        Get the Angular Velocity of this SwerveDrive
        
        :returns: float in radians per second
        """
        return self.getChassisSpeeds().omega
    
    # Get ChassisSpeeds
    def getChassisSpeeds(self) -> ChassisSpeeds:
        """
        Get the Current Chassis Speeds based on the Wheel Measurements
        
        :returns: ChassisSpeeds in meters per second velocity in x and y direction and rotations per
        """
        return self.getKinematics().toChassisSpeeds( self.getModuleStates() )
    
    # Get Module States
    def getModuleStates(self) -> typing.Tuple[ SwerveModuleState,
                                               SwerveModuleState,
                                               SwerveModuleState,
                                               SwerveModuleState ]:
        """
        Returns all of the SwerveModuleStates of the SwerveModules on this SwerveDrive

        :returns: Tuple of SwerveModuleStates (velocity, rotation)
        """
        return tuple( modules.getModuleState() for modules in self.modules )

    # Get Module Positions

    def getModulePositions(self) -> typing.Tuple[ SwerveModulePosition,
                                                  SwerveModulePosition,
                                                  SwerveModulePosition,
                                                  SwerveModulePosition ]:
        """
        Returns all of the SwerveModulePositions of the SwerveModules on this SwerveDrive

        :returns: Tuple of SwerveModulePosition (distance, rotation)
        """
        return tuple( modules.getModulePosition() for modules in self.modules )
    
    # Stop Drivetrain
    def stop(self): # -> CommandBase:
        """
        Stops this SwerveDrive
        """
        self.runChassisSpeeds( ChassisSpeeds(0,0,0) )
        
    ### Run SwerveDrive Functions
    def runPercentageInputs(self, x:float = 0.0, y:float = 0.0, r:float = 0.0) -> None:
        """
        Runs this SwerveDrive in x,y velocities and r rotations based on the maximum velocity characterized
        """
        veloc_x = x * self.maxVelocity.get()
        veloc_y = y * self.maxVelocity.get()
        veloc_r = r * self.maxAngularVelocity.get()

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

    # Run SwerveDrive using ChassisSpeeds
    def runChassisSpeeds(self, speeds:ChassisSpeeds, convertFieldRelative:bool = False) -> None:
        """
        Runs this SwerveDrive based on the provided ChassisSpeed
        """
        if convertFieldRelative: speeds = ChassisSpeeds.fromFieldRelativeSpeeds( speeds, self.getRobotAngle() ) # Needed for Trajectory State not being field relative
        self.ntChassisSpeedsNext.set( speeds )
        modStates = self.getKinematics().toSwerveModuleStates(speeds, Translation2d(0, 0)) # Convert to SwerveModuleState
        self.runSwerveModuleStates( modStates )

    # Run SwerveDrive using SwerveModuleStates
    def runSwerveModuleStates(self, states:typing.Tuple[ SwerveModuleState,
                                                         SwerveModuleState,
                                                         SwerveModuleState,
                                                         SwerveModuleState ]) -> None:
        """
        Runs this SwerveDrive based on provided SwerveModuleState.

        This method will optomize the SwerveModuleState prior to use to minimize the turning to less than 90 degrees
        """
        # Update Desired State for each Swerve Module
        optStates = SwerveDrive4Kinematics.desaturateWheelSpeeds(states, self.maxVelocity.get())
        for x in range(len(self.modules)):
            optimalState:SwerveModuleState = SwerveModuleState.optimize(
                optStates[x],
                self.modules[x].getModulePosition().angle
            )
            self.modules[x].setDesiredState( optimalState )

        # Logging
        self.ntSwerveModuleStatesNext.set( states )
        self.ntSwerveModuleStatesNextOptimized.set( optStates )
