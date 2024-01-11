"""
Description: Vision Camera Container Class
Version:  1
Date:  2024-01-10
"""

import typing
from ntcore import NetworkTable
#from wpimath.geometry import Pose2d, Pose3d

class VisionCamera:
    """
    VisionCamera Container Class
    """

    timestamps:typing.Tuple[float] = []
    frames:typing.List[typing.List] = []
    demoFrame:typing.Tuple[float] = []
    fps:float = 0.0

    def updateOutputs(self):
        """
        Update Output Logs
        """
        pass

    def toLog(self, table:NetworkTable):
        """
        Put Data Onto Network Tables
        """
        table.putNumberArray("Timestamps", self.timestamps)
        table.putNumber("FrameCount", len(self.frames))
        for i in range(len(self.frames)):
            table.putNumberArray(f"Frame/{i}", self.frames[i])
        table.putNumberArray("DemoFrame", self.demoFrame)
        table.putNumber("Fps", self.fps)

    def fromLog(self, table:NetworkTable):
        """
        Get Data From Network Tables
        """
        self.timestamps = table.getNumberArray("Timestamps", [])
        frameCount:int = int(table.getNumber("FrameCount", 0))
        self.frames:typing.List[typing.List] = []
        for i in range(frameCount):
            self.frames.append( table.getNumberArray(f"Frame/{i}", []) )
        self.demoFrame = table.getNumberArray("DemoFrame", [])
        self.fps = table.getNumber("Fps", 0)

    # def getPose2d(self) -> Pose2d:
    #     return self.lastPose2d
    # def getPose3d(self) -> Pose3d:
    #     return self.lastPose3d
    # def getTagPoses(self) -> typing.Tuple[Pose2d]:
    #     return self.lastLatency