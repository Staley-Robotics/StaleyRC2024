"""
Description: Vision Subsystem
Version:  1
Date:  2024-01-10

Dependencies:
- None
"""

# Built In Imports
import typing

# FRC imports
from commands2 import Subsystem
from ntcore import *
from wpilib import Timer, DriverStation
from wpimath.geometry import *
from wpimath.estimator import SwerveDrive4PoseEstimator

# Custom Imports
from .VisionCamera import VisionCamera

ambiguityThreshold = 0.15
fieldBorderMargin = 0.5
fieldLength = 15.98
fieldWidth = 8.21
zMargin = 0.75

class Vision(Subsystem):
    """
    Vision Subsystem
    """

    def __init__( self,
                  cameras:typing.Tuple[VisionCamera], 
                  odometryFunction:typing.Callable[[], SwerveDrive4PoseEstimator]):
        """
        Initialization
        """
        # Camera Configuration
        self.cameras:typing.Tuple[VisionCamera] = cameras
        self.cameraInputs:typing.Tuple[VisionCamera.VisionCameraInputs] = []
        for camera in self.cameras:
            self.cameraInputs.append( camera.VisionCameraInputs() )

        # Odometry Callable
        self.getOdometry = odometryFunction

        # NT Logging
        ntInst = NetworkTableInstance.getDefault()
        if not ntInst.hasSchema( "VisionCameraInputs" ):        
            self.ntSwerveModuleStatesCurrent = ntInst.getStructTopic( "/StartSchema/VisionCameraInputs", VisionCamera.VisionCameraInputs ).publish( PubSubOptions() )
            self.ntSwerveModuleStatesCurrent.set( VisionCamera.VisionCameraInputs() ) 
            self.ntSwerveModuleStatesCurrent.close()

        self.ntCameraInputs:typing.Tuple[StructPublisher] = []
        for x in range(len(self.cameras)):
            self.ntCameraInputs.append( ntInst.getStructTopic( f"/Vision/{self.cameras[x].name}", VisionCamera.VisionCameraInputs ).publish() )

        self.ntCameraOutputs:typing.Tuple[typing.Dict[str,StructPublisher]] = []
        for x in range(len(self.cameras)):
            self.ntCameraOutputs.append(
                {
                    "HasTargets": ntInst.getBooleanTopic( f"/Logging/Vision/{self.cameras[x].name}/HasTargets" ).publish(),
                    "LatencySecs": ntInst.getFloatTopic(  f"/Logging/Vision/{self.cameras[x].name}/LatencySecs" ).publish(),
                    "BlueRobotPose2d": ntInst.getStructTopic( f"/Logging/Vision/{self.cameras[x].name}/BlueRobotPose2d", Pose2d ).publish(),
                    "BlueRobotPose3d": ntInst.getStructTopic( f"/Logging/Vision/{self.cameras[x].name}/BlueRobotPose3d", Pose3d ).publish(),
                    "RedRobotPose2d": ntInst.getStructTopic( f"/Logging/Vision/{self.cameras[x].name}/RedRobotPose2d", Pose2d ).publish(),
                    "RedRobotPose3d": ntInst.getStructTopic( f"/Logging/Vision/{self.cameras[x].name}/RedRobotPose3d", Pose3d ).publish(),
                    "TagPoses":    ntInst.getStructArrayTopic( f"/Logging/Vision/{self.cameras[x].name}/TagPoses", Pose3d ).publish()
                }
            )

    def periodic(self):
        """
        Periodic Loop
        """
        for x in range(len(self.cameras)):
            # Logging Inputs
            self.cameras[x].updateInputs( self.cameraInputs[x] )
            self.ntCameraInputs[x].set( self.cameraInputs[x] )

            # Run VisionCamera objects
            self.cameras[x].run()
            
            # Loging Outputs
            if self.cameras[x].hasData:
                self.ntCameraOutputs[x]["HasTargets"].set( True )
                self.ntCameraOutputs[x]["LatencySecs"].set( value=self.cameras[x].latencySecs )
                self.ntCameraOutputs[x]["BlueRobotPose2d"].set( value=self.cameras[x].blueRobotPose2d )
                self.ntCameraOutputs[x]["BlueRobotPose3d"].set( value=self.cameras[x].blueRobotPose3d )
                self.ntCameraOutputs[x]["RedRobotPose2d"].set( value=self.cameras[x].redRobotPose2d )
                self.ntCameraOutputs[x]["RedRobotPose3d"].set( value=self.cameras[x].redRobotPose3d )
                #self.ntCameraOutputs[x]["TagPoses"].set( value=[] )
                
                # Fuse Data with Odometry
                if DriverStation.getAlliance() == DriverStation.Alliance.kBlue:
                    self.getOdometry().addVisionMeasurement(
                        self.cameras[x].blueRobotPose2d,
                        Timer.getFPGATimestamp() - self.cameras[x].latencySecs
                    )
                elif DriverStation.getAlliance() == DriverStation.Alliance.kRed:
                    self.getOdometry().addVisionMeasurement(
                        self.cameras[x].redRobotPose2d,
                        Timer.getFPGATimestamp() - self.cameras[x].latencySecs
                    )
            else:
                self.ntCameraOutputs[x]["HasTargets"].set( False )


            

