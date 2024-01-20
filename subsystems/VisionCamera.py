"""
Description: Vision Camera Container Class
Version:  1
Date:  2024-01-10
"""
# Build In Imports
import typing
import dataclasses

# FRC Imports
from ntcore import NetworkTable
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
        A WPIStruct Object that contains all SwerveModule Data.
        This is intended to simplify logging of this data.
        """
        connected:bool = False
        #timestamps:typing.ClassVar[list[int]] = []
        #frames:typing.ClassVar[list[int]] = []
        #demoFrame:typing.ClassVar[list[int]] = []
        #fps:float = 0.0

    name:str = "VisionCamera"

    hasData:bool = False
    latencySecs:float = 0.0
    blueRobotPose2d:Pose2d = Pose2d()
    blueRobotPose3d:Pose3d = Pose3d()
    redRobotPose2d:Pose2d = Pose2d()
    redRobotPose3d:Pose3d = Pose3d()
    tagPoses:typing.Tuple[Pose2d] = []

    def updateInputs(self, inputs:VisionCameraInputs):
        """
        Update Input Logs
        """
        pass

    def run(self):
        """
        Runtime Method for the Camera
        """
        pass
