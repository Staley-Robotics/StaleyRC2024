"""
Description: Limelight Subsystem
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
from wpimath.geometry import Rotation2d, Pose2d
from wpimath.estimator import SwerveDrive4PoseEstimator
from ntcore import *

# Our Imports

### Constants

### Class: SwerveDrive
class Limelight(Subsystem):
    """
    Limelight Subsystem
    """
    def __init__(self, name:str, odometryFunction:typing.Callable[[], SwerveDrive4PoseEstimator]):
        """
        Initialization
        """
        super().__init__()
        self.name = name
        self.table:NetworkTable = NetworkTableInstance.getDefault().getTable( name )
        self.getOdometry = odometryFunction
        
        # Push Configuration to Limelight Here
        ### No code yet

        # tId Subscriber
        self.tidSubscriber:IntegerSubscriber = self.table.getIntegerTopic("tid").subscribe(
            -1,
            PubSubOptions.keepDuplicates(True),
            PubSubOptions.sendAll(True)
        )

        # Raw Bot Pose Data Subscriber
        self.poseRedSubscriber:DoubleArraySubscriber = self.table.getDoubleArrayTopic("botpose").subscribe(
            float[0.0],
            PubSubOptions.keepDuplicates(True),
            PubSubOptions.sendAll(True)
        )

        # Red Pose Data Subscriber
        self.poseRedSubscriber:DoubleArraySubscriber = self.table.getDoubleArrayTopic("botpose_wpired").subscribe(
            float[0.0],
            PubSubOptions.keepDuplicates(True),
            PubSubOptions.sendAll(True)
        )
        # Blue Pose Data Subscriber
        self.poseBlueSubscriber:DoubleArraySubscriber = self.table.getDoubleArrayTopic("botpose_wpiblue").subscribe(
            float[0.0],
            PubSubOptions.keepDuplicates(True),
            PubSubOptions.sendAll(True)
        )

        # Frames Per Second Subscriber
        self.fpsSubscriber = self.table.getDoubleTopic("fps").subscribe(0)

        # Timer for Disconnected Status
        self.disconnectedTimer = Timer()
        self.disconnectedTimer.start()

    def periodic(self):
        """
        Periodic Loop Updates
        """
        
        # # Check for Valid Limelight Data
        # aprilTag = self.table.getNumber("tid",-1) 
        # if int(aprilTag) == -1: return
        
        # # Check for Alliance Settings, Get Bot Pose Data from Limelight
        # match DriverStation.getAlliance():
        #     case DriverStation.Alliance.kRed:
        #         botPose = self.table.getNumberArray("botpose_wpired", None)
        #     case DriverStation.Alliance.kBlue:
        #         botPose = self.table.getNumberArray("botpose_wpiblue", None)
        #     case _:
        #         return None

        # # Translate Bot Pose Data to Pose2d
        # if botPose == None: return
        # llx = botPose[0]
        # lly = botPose[1]
        # llz = botPose[5]
        # llt = botPose[6]
        # llPose = Pose2d(llx, lly, Rotation2d(0).fromDegrees(llz))


        # # Get Time Offset Information
        # llOffset = Timer.getFPGATimestamp() - (llt/1000)
        
        # # Update Odometry
        # self.getOdometry().addVisionMeasurement(
        #     llPose,
        #     llOffset
        # )

        ### New Code using all Subscriber Table Data (more accurate?)
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
            
            # Update Odometry with Vision Measurements
            self.getOdometry().addVisionMeasurement(
                Pose2d(frame[0], frame[1], Rotation2d(0).fromDegrees(frame[5])),
                tstamp - (frame[6]/1000)
            )

        # Logging
        NetworkTableInstance.getDefault().getTable("Logging").putNumberArray(
            f"{self.name}/frame",
            frameList
        )  
        NetworkTableInstance.getDefault().getTable("Logging").putNumberArray(
            f"{self.name}/frameTimestamp",
            tstampList
        )  

        NetworkTableInstance.getDefault().getTable("Logging").putNumberArray(
            f"{self.name}/fps",
            self.fpsSubscriber.get()
        ) 
            
        # Disconnected Alerting!
        if tidLength > 0:
            self.disconnectedTimer.reset()

        if self.disconnectedTimer.hasElapsed( 0.5 ):
            print( f"Limelight {self.name} - Disconnected!")

              
