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
        super().__init__()
        self.name = name
        self.table:NetworkTable = NetworkTableInstance.getDefault().getTable( name )
        
        # Push Configuration to Limelight Here
        ### No code yet

        # tId Subscriber
        self.tidSubscriber:IntegerSubscriber = self.table.getIntegerTopic("tid").subscribe(
            -1,
            PubSubOptions( keepDuplicates = True, sendAll = True )
        )

        # Raw Bot Pose Data Subscriber
        self.poseRedSubscriber:DoubleArraySubscriber = self.table.getDoubleArrayTopic("botpose").subscribe(
            [],
            PubSubOptions( keepDuplicates = True, sendAll = True )
        )

        # Red Pose Data Subscriber
        self.poseRedSubscriber:DoubleArraySubscriber = self.table.getDoubleArrayTopic("botpose_wpired").subscribe(
            [],
            PubSubOptions( keepDuplicates = True, sendAll = True )
        )
        # Blue Pose Data Subscriber
        self.poseBlueSubscriber:DoubleArraySubscriber = self.table.getDoubleArrayTopic("botpose_wpiblue").subscribe(
            [],
            PubSubOptions( keepDuplicates = True, sendAll = True )
        )

        # Frames Per Second Subscriber
        self.fpsSubscriber = self.table.getDoubleTopic("fps").subscribe(0)

        # Timer for Disconnected Status
        self.disconnectedTimer = Timer()
        self.disconnectedTimer.start()

    def updateOutputs(self):
        frameList = []
        tstampList = []

        # Get Queues
        sub:DoubleArraySubscriber = self.poseRedSubscriber if DriverStation.getAlliance() == DriverStation.Alliance.kRed else self.poseBlueSubscriber
        subQueue = sub.readQueue()
        tidQueue = self.tidSubscriber.readQueue()
        tidLength = len(tidQueue)

        # Process Queues
        for x in range(tidLength):
            # If Invalid Value, Skip
            if tidQueue[x].value == -1: continue

            # Get BotPose Data
            frame = subQueue[x].value
            tstamp = subQueue[x].time / 1000000.0
            frameList.append(frame)
            tstampList.append(tstamp)
            
        # Logging Raw Frame Data
        NetworkTableInstance.getDefault().getTable("Limelight").putNumberArray(
            f"{self.name}/frame",
            frameList
        )  
        NetworkTableInstance.getDefault().getTable("Limelight").putNumberArray(
            f"{self.name}/frameTimestamp",
            tstampList
        )  

        NetworkTableInstance.getDefault().getTable("Limelight").putNumber(
            f"{self.name}/fps",
            self.fpsSubscriber.get( -1 )
        ) 
       
        # Disconnected Alerting!
        if tidLength > 0:
            self.disconnectedTimer.reset()

        if self.disconnectedTimer.hasElapsed( 0.5 ):
            print( f"Limelight {self.name} - Disconnected!")
