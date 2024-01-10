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
    __ntTbl__ = NetworkTableInstance.getDefault().getTable("SwerveDrive")

    # Initialization
    def __init__( self,
                  modules:typing.Tuple[ SwerveModule,
                                        SwerveModule,
                                        SwerveModule,
                                        SwerveModule ],
                  gyro:Gyro=Gyro() ):
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

        # Logging Current Chassis Speeds
        cSpeed = self.getChassisSpeeds()
        NetworkTableInstance.getDefault().getTable("Logging").putNumberArray( 
            "ChassisSpeeds/Current",
            [ cSpeed.vx, cSpeed.vy, cSpeed.omega ]
        )

        # Logging Measures SwerveModuleStates
        measuredState = list()
        for state in self.getModuleStates():
            measuredState.append( state.angle.radians() )
            measuredState.append( state.speed )
        NetworkTableInstance.getDefault().getTable("Logging").putNumberArray(
            "SwerveModuleStates/Current",
            measuredState
        )        

        # Odometry from Module Position Data
        pose = self.getOdometry().updateWithTime(
            Timer.getFPGATimestamp(),
            self.gyro.getRotation2d(),
            self.getModulePositions()
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
        pass

    ### Drive Based Functions
    # Returns Field Relative Status
    def isFieldRelative(self):
        return self.fieldRelative.get()

    # Kinematics
    def getKinematics(self) -> SwerveDrive4Kinematics:
        return self.kinematics
       
    # Get Odometry Object
    def getOdometry(self) -> SwerveDrive4PoseEstimator:
        return self.odometry

    # Get Pose
    def getPose(self) -> Pose2d:
        return self.getOdometry().getEstimatedPosition()
    
    # Get Heading of Rotation
    def getRobotAngle(self) -> Rotation2d:
        return self.gyro.getRotation2d()

    # Get Angular Velocity
    def getRotationVelocity(self) -> float:
        return self.getChassisSpeeds().omega

    # Get ChassisSpeeds
    def getChassisSpeeds(self) -> ChassisSpeeds:
        return self.getKinematics().toChassisSpeeds( self.getModuleStates() )
    
    # Get Module States
    def getModuleStates(self) -> typing.Tuple[ SwerveModuleState,
                                               SwerveModuleState,
                                               SwerveModuleState,
                                               SwerveModuleState ]:
        return tuple( modules.getModuleState() for modules in self.modules )

    # Get Module Positions
    def getModulePositions(self) -> typing.Tuple[ SwerveModulePosition,
                                                  SwerveModulePosition,
                                                  SwerveModulePosition,
                                                  SwerveModulePosition ]:
        return tuple( modules.getModulePosition() for modules in self.modules )
    
    # Stop Drivetrain
    def stop(self): # -> CommandBase:
        self.runChassisSpeeds( ChassisSpeeds(0,0,0) )
        
    ### Run SwerveDrive Functions
    def runPercentageInputs(self, x:float = 0.0, y:float = 0.0, r:float = 0.0) -> None:
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
        if convertFieldRelative: speeds = ChassisSpeeds.fromFieldRelativeSpeeds( speeds, self.getRobotAngle() ) # Needed for Trajectory State not being field relative
        rotationCenter = Translation2d(0, 0)
        NetworkTableInstance.getDefault().getTable("Logging").putNumberArray( 
            "ChassisSpeeds/Next",
            [ speeds.vx, speeds.vy, speeds.omega ]
        )
        modStates = self.getKinematics().toSwerveModuleStates(speeds, rotationCenter) # Convert to SwerveModuleState
        self.runSwerveModuleStates( modStates )

    # Run SwerveDrive using SwerveModuleStates
    def runSwerveModuleStates(self, states:typing.Tuple[ SwerveModuleState,
                                                         SwerveModuleState,
                                                         SwerveModuleState,
                                                         SwerveModuleState ]) -> None:
        """
        """
        desiredValues = list()
        optimizedValues = list()

        # Update Desired State for each Swerve Module
        modStates = SwerveDrive4Kinematics.desaturateWheelSpeeds(states, self.maxVelocity.get())
        for x in range(len(self.modules)):
            # Calculate Optimal State
            optimalState:SwerveModuleState = SwerveModuleState.optimize(
                modStates[x],
                self.modules[x].getModulePosition().angle
            )

            # Set Values
            self.modules[x].setDesiredState( optimalState )

            # Desired Values
            desiredValues.append( modStates[x].angle.radians() )
            desiredValues.append( modStates[x].speed )
            
            # Optimized Values
            
            optimizedValues.append( optimalState.angle.radians() )
            optimizedValues.append( optimalState.speed )
            
        # Logging
        NetworkTableInstance.getDefault().getTable("Logging").putNumberArray( f"SwerveModuleStates/NextDesired", desiredValues )
        NetworkTableInstance.getDefault().getTable("Logging").putNumberArray( f"SwerveModuleStates/NextOptimized", optimizedValues )
