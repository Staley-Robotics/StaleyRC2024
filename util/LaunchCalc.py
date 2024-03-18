import math
import typing

from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpimath.geometry import Pose2d, Rotation2d

from util.CrescendoUtil import CrescendoUtil
from util.NTTunableFloat import NTTunableFloat

class LaunchCalc(Subsystem):
    def __init__(self, getPose:typing.Callable[[], Pose2d]):
        self.aimAdjust = NTTunableFloat( "/Config/PivotPositions/AutoAimAdjust", 0.0, persistent=True )

        self.getPose = getPose
        
        self.distance = 0
        self.launchAngle = 0
        self.rotation = Rotation2d(0)

        self.ntLogger = NetworkTableInstance.getDefault().getTable( "/Logging/LaunchCalc" )

    def periodic(self):
        robotPose = self.getPose()
        targetPose = Pose2d( CrescendoUtil.getSpeakerTarget(), Rotation2d(0) )
        relativePose = robotPose.relativeTo( targetPose )
        
        targetH = CrescendoUtil.getSpeakerHeight()
        pivotH = CrescendoUtil.getRobotPivotHeight()

        self.distance = relativePose.translation().norm()
        self.rotation = relativePose.translation().angle()
        self.launchAngle = math.degrees( math.atan( ( targetH - pivotH ) / self.distance ) )
        self.launchAngleAdj = self.launchAngle + self.aimAdjust.get()

        self.ntLogger.putNumber( "Distance", self.distance )
        self.ntLogger.putNumber( "RotationRadians", self.rotation.radians() )
        self.ntLogger.putNumber( "RotationDegrees", self.rotation.degrees() )
        self.ntLogger.putNumber( "LaunchAngle", self.launchAngle )
        self.ntLogger.putNumber( "LaunchAngleAdj", self.launchAngleAdj )

    def getRotateAngle(self) -> Rotation2d:
        return self.rotation

    def getLaunchAngle(self) -> float:
        return self.launchAngleAdj

    def setPoseFunc(self):
        pass

    def setPivotFunc(self):
        pass