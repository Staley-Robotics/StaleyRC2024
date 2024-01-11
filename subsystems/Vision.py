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
from wpilib import Timer
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
                  modules:typing.Tuple[VisionCamera], 
                  odometryFunction:typing.Callable[[], SwerveDrive4PoseEstimator]):
        """
        Initialization
        """
        self.modules:typing.Tuple[VisionCamera] = modules
        self.getOdometry = odometryFunction

    def periodic(self):
        """
        Periodic Loop
        """
        # Loop through all Modules
        for m in self.modules:
            # Update Input Logs
            m.updateOutputs()

            # Validate Frames and Timestamps can coexist
            if len(m.frames) != len (m.timestamps):
                continue
            
            # Update Odometry with Vision Measurements
            for i in range(len(m.frames)):
                tstamp = m.timestamps[i]
                f = m.frames[i]
                lastPose2d = Pose2d(f[0], f[1], Rotation2d(0).fromDegrees(f[5]))
                self.getOdometry().addVisionMeasurement(
                    lastPose2d,
                    tstamp - (f[6]/1000)
                )

