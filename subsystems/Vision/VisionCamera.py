"""
Description: Vision Camera Container Class
Version:  1
Date:  2024-01-10
"""
# Build In Imports
import typing
import dataclasses

# FRC Imports
from wpilib import DriverStation
from wpimath.geometry import Pose2d, Pose3d
import wpiutil.wpistruct

class VisionCamera:
    """
    VisionCamera Container Class
    """
   
    @wpiutil.wpistruct.make_wpistruct(name="VisionCameraInputs")
    @dataclasses.dataclass
    class VisionCameraInputs:
        """
        A WPIStruct Object that contains all Vision Data.
        This is intended to simplify logging of this data.
        """
        connected:bool = False
        #timestamps:typing.ClassVar[list[int]] = []
        #frames:typing.ClassVar[list[int]] = []
        #demoFrame:typing.ClassVar[list[int]] = []
        #fps:float = 0.0
        blueLastTimestamp:float = 0.0
        blueLatencySecs:float = 0.0
        blueDistance:float = 0.0
        blueRobotPose2d:Pose2d = dataclasses.field( default_factory= Pose2d )
        blueRobotPose3d:Pose3d = dataclasses.field( default_factory= Pose3d )
        redLastTimestamp:float = 0.0
        redLatencySecs:float = 0.0
        redDistance:float = 0.0
        redRobotPose2d:Pose2d = dataclasses.field( default_factory= Pose2d )
        redRobotPose3d:Pose3d = dataclasses.field( default_factory= Pose3d )
        #tagPoses:typing.Tuple[Pose2d] = None #[]

    name:str = "VisionCamera"

    def updateInputs(self, inputs:VisionCameraInputs):
        """
        Update Input Logs
        """
        pass

    def run(self):
        pass

    def getPoseQueue(self, alliance:DriverStation.Alliance):
        return []