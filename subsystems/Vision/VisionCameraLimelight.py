"""
Description: Limelight Camera
Version:  1
Date:  2024-01-10

Dependencies:
- None
"""

### Imports
# Python Imports
import typing

# FRC Component Imports
from commands2 import Subsystem
from wpilib import Timer, DriverStation
from wpimath.geometry import Rotation2d, Pose2d, Pose3d, Translation3d, Rotation3d
from wpimath.estimator import SwerveDrive4PoseEstimator
from ntcore import *

# Our Imports
from .VisionCamera import VisionCamera
### Constants

### Class: SwerveDrive
class VisionCameraLimelight(VisionCamera):
    """
    Limelight Subsystem
    """
    def __init__(self, name:str):
        """
        Initialization
        """
        self.name = name
        self.table:NetworkTable = NetworkTableInstance.getDefault().getTable( name )
        
        # Push Configuration to Limelight Here
        ### No code yet

        # Timer for Disconnected Status
        self.disconnectedTimer = Timer()
        self.disconnectedTimer.start()

    def updateInputs(self, inputs:VisionCamera.VisionCameraInputs):
        """
        Update Input Logs
        """
        tid:int = int( self.table.getNumber("tid", -2) )

        # Disconnected Alerting!
        if tid != -2:
            self.disconnectedTimer.reset()
            inputs.connected = True

        if self.disconnectedTimer.hasElapsed( 1.0 ):
            inputs.connected = False

    def run(self):
        tid = int( self.table.getNumber("tid", -1) )

        if tid != -1:
            # Mark HasData True
            self.hasData = True
            # Red Pose Data            
            redPose = self.table.getNumberArray("botpose_wpired", [])
            if len(redPose) == 7:
                self.redRobotPose2d = Pose2d( redPose[0], redPose[1], Rotation2d().fromDegrees(redPose[5]) )
                self.redRobotPose3d = Pose3d( Translation3d(redPose[0], redPose[1], redPose[2]), Rotation3d(redPose[3], redPose[4], redPose[5]) )
                self.latencySecs = ((redPose[6])/1000)
            # Blue Pose Data
            bluePose = self.table.getNumberArray("botpose_wpiblue", [])
            if len(bluePose) == 7:
                self.blueRobotPose2d = Pose2d( bluePose[0], bluePose[1], Rotation2d().fromDegrees(bluePose[5]) )
                self.blueRobotPose3d = Pose3d( Translation3d(bluePose[0], bluePose[1], bluePose[2]), Rotation3d(bluePose[3], bluePose[4], bluePose[5]) )
                self.latencySecs = ((bluePose[6])/1000)
            # Tag Poses
            self.tagPoses = []
        else:
            # Mark HasData False
            self.hasData = False

