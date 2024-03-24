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
class VisionCameraLimelight3(VisionCamera):
    """
    Limelight Subsystem
    """
    def __init__(self, name:str):
        """
        Initialization
        """
        self.name = name
        self.table:NetworkTable = NetworkTableInstance.getDefault().getTable( name )
        self.wpiblue = self.table.getDoubleArrayTopic("botpose_wpiblue").subscribe()
        self.wpired = self.table.getDoubleArrayTopic("botpose_wpired").subscribe()
        
        # Push Configuration to Limelight Here
        ### No code yet

        # Timer for Disconnected Status
        # self.disconnectedTimer = Timer()
        # self.disconnectedTimer.start()

    def updateInputs(self, inputs:VisionCamera.VisionCameraInputs):
        """
        Update Input Logs
        """
        tid:int = int( self.table.getNumber("tid", -2) )

        if tid == -2:
            # Disconnected!
            inputs.connected = False
            inputs.blueHasData = False
            inputs.redHasData = False
        elif tid == -1:
            # Has No Data!
            inputs.connected = True
            inputs.blueHasData = False
            inputs.redHasData = False
        else:
            # Has Data!
            inputs.connected = True

            # Blue Pose Data
            bluePose = self.table.getNumberArray("botpose_wpiblue", [])
            if len(bluePose) != 11:
                inputs.blueHasData = False
            elif bluePose[0] == 0 and bluePose[1] == 0 and bluePose[5] == 0:
                inputs.blueHasData = False
            else:
                inputs.blueHasData = True
                inputs.blueRobotPose2d = Pose2d( bluePose[0], bluePose[1], Rotation2d().fromDegrees(bluePose[5]) )
                inputs.blueRobotPose3d = Pose3d( Translation3d(bluePose[0], bluePose[1], bluePose[2]), Rotation3d(bluePose[3], bluePose[4], bluePose[5]) )
                inputs.blueLatencySecs = ((bluePose[6])/1000)
            
            # Red Pose Data
            redPose = self.table.getNumberArray("botpose_wpired", [])
            if len(bluePose) != 11:
                inputs.redHasData = False
            elif bluePose[0] == 0 and bluePose[1] == 0 and bluePose[5] == 0:
                inputs.redHasData = False
            else:
                inputs.redHasData = True
                inputs.redRobotPose2d = Pose2d( redPose[0], redPose[1], Rotation2d().fromDegrees(redPose[5]) )
                inputs.redRobotPose3d = Pose3d( Translation3d(redPose[0], redPose[1], redPose[2]), Rotation3d(redPose[3], redPose[4], redPose[5]) )
                inputs.redLatencySecs = ((redPose[6])/1000)

    def run(self):
        pass
