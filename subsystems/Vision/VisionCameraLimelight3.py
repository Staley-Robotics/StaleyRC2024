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
from wpimath.units import degreesToRadians
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
        self.wpiblue:DoubleArraySubscriber = self.table.getDoubleArrayTopic("botpose_wpiblue").subscribe([0.0])
        self.wpired:DoubleArraySubscriber = self.table.getDoubleArrayTopic("botpose_wpired").subscribe([0.0])
        
        # Push Configuration to Limelight Here
        ### No code yet

        # Timer for Disconnected Status
        # self.disconnectedTimer = Timer()
        # self.disconnectedTimer.start()

        self.blueQueue = []
        self.redQueue = []

        self.logger = NetworkTableInstance.getDefault().getTable( f"/Logging2/{name}" )

    def updateInputs(self, inputs:VisionCamera.VisionCameraInputs):
        """
        Update Input Logs
        """
        tid:int = int( self.table.getNumber("tid", -2) )

        if tid == -2:
            inputs.connected = False # Disconnected!
        else:
            inputs.connected = True # Connected

        # Blue Pose Data
        bCnt = len( self.blueQueue )
        if bCnt != 0:
            inputs.blueLastTimestamp = self.blueQueue[bCnt-1]['poseTimestamp']
            inputs.blueLatencySecs = self.blueQueue[bCnt-1]['latency']
            inputs.blueDistance = self.blueQueue[bCnt-1]['distance']
            inputs.blueRobotPose2d = self.blueQueue[bCnt-1]['pose2d']
            inputs.blueRobotPose3d = self.blueQueue[bCnt-1]['pose3d']
        
        # Red Pose Data
        rCnt = len( self.redQueue )
        if rCnt != 0:
            inputs.redLastTimestamp = self.redQueue[rCnt-1]['poseTimestamp']
            inputs.redLatencySecs = self.redQueue[rCnt-1]['latency']
            inputs.redDistance = self.redQueue[rCnt-1]['distance']
            inputs.redRobotPose2d = self.redQueue[rCnt-1]['pose2d']
            inputs.redRobotPose3d = self.redQueue[rCnt-1]['pose3d']

    def run(self):
        # Get Updated Queue Data
        self.blueQueue = self.processQueue( self.wpiblue.readQueue() )
        self.redQueue = self.processQueue( self.wpired.readQueue() )

        # Log Raw Data
        # if len(self.blueQueue) != 0:
        #     self.logger.putString( "BlueQueue", f"{self.blueQueue}" )

        # if len(self.redQueue) != 0:
        #     self.logger.putString( "RedQueue", f"{self.redQueue}")

    def processQueue(self, queue:list[TimestampedDoubleArray]) -> list:
        returnQueue = []
        for i in range(len(queue)):
            t = queue[i].time
            tx = queue[i].value[0]
            ty = queue[i].value[1]
            tz = queue[i].value[2]
            rr = degreesToRadians( queue[i].value[3] )
            rp = degreesToRadians( queue[i].value[4] )
            ry = degreesToRadians( queue[i].value[5] )
            d = queue[i].value[9]
            l = queue[i].value[6]

            if tx == 0.0 and ty == 0.0 and ry == 0.0:
                continue

            returnQueue.append(
                {
                    "poseTimestamp": (t / 1000000.0) - ( l / 1000 ), 
                    "distance": d,
                    "latency": l / 1000,
                    "pose2d": Pose2d( tx, ty, Rotation2d( ry ) ),
                    "pose3d": Pose3d( Translation3d( tx, ty, tz ), Rotation3d( rr, rp, ry ) )
                }
            )
        
        return returnQueue
    
    def getPoseQueue( self, alliance:DriverStation.Alliance ):
        match alliance:
            case DriverStation.Alliance.kBlue:
                return self.blueQueue
            case DriverStation.Alliance.kRed:
                return self.redQueue
            case _:
                return []
            
