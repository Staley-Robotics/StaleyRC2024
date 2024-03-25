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
from util import *

# ambiguityThreshold = 0.15
# fieldBorderMargin = 0.5
# fieldLength = 15.98
# fieldWidth = 8.21
# zMargin = 0.75

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
        self.offline = NTTunableBoolean( "/DisableSubsystem/Vision", False, persistent=True )
        self.stdDev = NTTunableFloat( "/Config/Vision/StdDev", 1.25, persistent=True )

        # Camera Configuration
        self.cameras:typing.Tuple[VisionCamera] = cameras
        self.cameraInputs:typing.Tuple[VisionCamera.VisionCameraInputs] = []
        for camera in self.cameras:
            self.cameraInputs.append( camera.VisionCameraInputs() )

        # Odometry Callable
        self.getOdometry = odometryFunction

        # NT Logging
        ntInst = NetworkTableInstance.getDefault()
        self.ntCameraInputs:typing.Tuple[StructPublisher] = []
        for x in range(len(self.cameras)):
            self.ntCameraInputs.append( ntInst.getStructTopic( f"/Vision/{self.cameras[x].name}", VisionCamera.VisionCameraInputs ).publish() )

    def periodic(self):
        """
        Periodic Loop
        """
        # Override for Turning Vision on and Off
        if self.offline.get(): return

        for x in range(len(self.cameras)):
            # Logging Inputs
            self.cameras[x].updateInputs( self.cameraInputs[x] )
            self.ntCameraInputs[x].set( self.cameraInputs[x] )

            # Run
            self.cameras[x].run()

            # Fuse Data with Odometry
            poses = self.cameras[x].getPoseQueue( DriverStation.getAlliance() )
            for y in range(len(poses)):
                self.getOdometry().addVisionMeasurement(
                    poses[y]['pose2d'],
                    poses[y]['poseTimestamp'],
                    [ self.stdDev.get(), self.stdDev.get(), self.stdDev.get() ]
                )




            

