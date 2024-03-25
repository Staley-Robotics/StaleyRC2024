import math
import typing

from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpimath.geometry import Pose2d, Rotation2d

from util.CrescendoUtil import CrescendoUtil
from util.NTTunableFloat import NTTunableFloat
from util.NTTunableBoolean import NTTunableBoolean

class LaunchCalc(Subsystem):
    def __init__(self, getPose:typing.Callable[[], Pose2d]):
        self.aimAdjust = NTTunableFloat( "/Config/LaunchCalc/AutoLaunchAngleAdjust", 0.0, persistent=True )
        self.autoLaunch = NTTunableBoolean( "/Config/LaunchCalc/AutoLaunch", False, persistent=True )
        self.autoLaunchDistance = NTTunableFloat( "/Config/LaunchCalc/AutoLaunchDistance", 3.0, persistent=True )
        self.autoLaunchVariance = NTTunableFloat( "/Config/LaunchCalc/AutoLaunchVariance", 5.0, persistent=True )

        self.getPose = getPose
        
        self.distance = 0
        self.launchAngle = 0
        self.rotation = Rotation2d(0)

        self.ntLogger = NetworkTableInstance.getDefault().getTable( "/Logging/LaunchCalc" )

    def periodic(self):
        robotPose = self.getPose()
        targetPose = Pose2d( CrescendoUtil.getSpeakerTarget(), Rotation2d(0) )
        relativePose:Pose2d = robotPose.relativeTo( targetPose )
        
        targetH = CrescendoUtil.getSpeakerHeight()
        pivotH = CrescendoUtil.getRobotPivotHeight()

        self.distance = relativePose.translation().norm()
        self.rotation = relativePose.translation().angle()
        self.rotationVariance = robotPose.rotation().degrees() - self.rotation.degrees()
        self.launchAngle = math.degrees( math.atan( ( targetH - pivotH ) / self.distance ) )
        self.launchAngleAdj = self.launchAngle + self.aimAdjust.get()

        self.ntLogger.putNumber( "Distance", self.distance )
        self.ntLogger.putNumber( "RotationVariance", self.rotationVariance )
        self.ntLogger.putNumber( "RotationRadians", self.rotation.radians() )
        self.ntLogger.putNumber( "RotationDegrees", self.rotation.degrees() )
        self.ntLogger.putNumber( "LaunchAngle", self.launchAngle )
        self.ntLogger.putNumber( "LaunchAngleAdj", self.launchAngleAdj )
        self.ntLogger.putBoolean( "AutoLaunchInRange", self.isAutoLaunchInRange() )

    def getRotateAngle(self) -> Rotation2d:
        return self.rotation

    def getRotationVariance(self) -> float:
        return self.rotationVariance

    def getLaunchAngle(self) -> float:
        return self.launchAngleAdj

    def getDistance(self) -> float:
        return self.distance

    def setPoseFunc(self):
        pass

    def setPivotFunc(self):
        pass

    def isAutoLaunchInRange(self) -> bool:
        return (
            self.getRotationVariance() < self.autoLaunchVariance.get() and
            self.getDistance() < self.autoLaunchDistance.get()
        )
    
    def isAutoLaunchApproved(self) -> bool:
        return (
            self.autoLaunch.get() and
            self.isAutoLaunchInRange()
        )