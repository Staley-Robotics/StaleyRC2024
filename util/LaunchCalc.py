import math
import typing
from enum import Enum

from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpimath.geometry import Pose2d, Rotation2d

from util.CrescendoUtil import CrescendoUtil
from util.NTTunableFloat import NTTunableFloat
from util.NTTunableBoolean import NTTunableBoolean

class LaunchCalc(Subsystem):
    class Targets(Enum):
        SPEAKER = 0
        AMP = 1
        TRAP1 = 2
        TRAP2 = 3
        TRAP3 = 4

    def __init__(self, getPose:typing.Callable[[], Pose2d]):
        self.autoLaunch = NTTunableBoolean( "/Config/LaunchCalc/AutoLaunch", False, persistent=True )
        self.speakerRotationRange = NTTunableFloat( "/Config/LaunchCalc/Speaker/RotationErrorRange", 2.5, persistent=True )
        self.speakerDistanceFar = NTTunableFloat( "/Config/LaunchCalc/Speaker/RangeFar", 10.0, persistent=True )
        self.speakerDistanceNear = NTTunableFloat( "/Config/LaunchCalc/Speaker/RangeNear", 7.0, persistent=True )
        self.speakerDistanceAuto = NTTunableFloat( "/Config/LaunchCalc/Speaker/RangeAuto", 3.0, persistent=True )
        self.ampRotationRange = NTTunableFloat( "/Config/LaunchCalc/Amp/RotationErrorRange", 1.0, persistent=True )
        self.ampDistanceFar = NTTunableFloat( "/Config/LaunchCalc/Amp/RangeFar", 1.0, persistent=True )
        self.ampDistanceNear = NTTunableFloat( "/Config/LaunchCalc/Amp/RangeNear", 0.75, persistent=True )
        self.ampDistanceAuto = NTTunableFloat( "/Config/LaunchCalc/Amp/RangeAuto", 0.25, persistent=True )
        self.aimAdjust = NTTunableFloat( "/Config/LaunchCalc/AimAdjust", 0.0, persistent=True )
        
        self.getPose = getPose
        
        self.target:LaunchCalc.Targets = LaunchCalc.Targets.SPEAKER
        self.distance = 0
        self.launchAngle = 0
        self.rotation = Rotation2d(0)

        self.ntLoggerState = NetworkTableInstance.getDefault().getTable( "/Logging/LaunchCalcState" )
        self.ntLoggerData = NetworkTableInstance.getDefault().getTable( "/Logging/LaunchCalcData" )

    def periodic(self):
        # Current Pose
        robotPose = self.getPose()
        pivotH = CrescendoUtil.getRobotPivotHeight()

        # Get Target Pose Data
        targetPose = Pose2d()
        targetH = 0
        match self.getTarget():
            case LaunchCalc.Targets.SPEAKER:
                targetPose = CrescendoUtil.getSpeakerPose()
                targetH = CrescendoUtil.getSpeakerHeight()
            case LaunchCalc.Targets.AMP:
                targetPose = CrescendoUtil.getAmpPose()
                targetH = CrescendoUtil.getAmpHeight()
        
        # Relative Pose Data
        relativePose:Pose2d = robotPose.relativeTo( targetPose )

        # Get Distance from Target
        self.distance = relativePose.translation().norm()
        
        # Get Rotation to Target
        self.rotation = relativePose.translation().angle()
        match self.getTarget():
            case LaunchCalc.Targets.AMP:
                self.rotation = targetPose.rotation()

        # Calculations
        self.rotationVariance = abs( robotPose.rotation().degrees() - self.rotation.degrees() )
        self.launchAngle = math.degrees( math.atan( ( targetH - pivotH ) / self.distance ) )
        self.launchAngleAdj = self.launchAngle + self.aimAdjust.get()

        # Logging
        self.ntLoggerState.putBoolean( "isTargetSpeaker", self.isTarget( LaunchCalc.Targets.SPEAKER ) )
        self.ntLoggerState.putBoolean( "inRangeFar", self.inFarRange() )
        self.ntLoggerState.putBoolean( "inRangeNear", self.inNearRange() )
        self.ntLoggerState.putBoolean( "inRangeAuto", self.inAutoRange() )
        self.ntLoggerState.putBoolean( "inRotationRange", self.inRotationRange() )
        self.ntLoggerState.putBoolean( "AutoLaunchInRange", self.isAutoLaunchInRange() )

        self.ntLoggerData.putNumber( "Distance", self.distance )
        self.ntLoggerData.putNumber( "RotationVariance", self.rotationVariance )
        self.ntLoggerData.putNumber( "RotationRadians", self.rotation.radians() )
        self.ntLoggerData.putNumber( "RotationDegrees", self.rotation.degrees() )
        self.ntLoggerData.putNumber( "LaunchAngle", self.launchAngle )
        self.ntLoggerData.putNumber( "LaunchAngleAdj", self.launchAngleAdj )
        
    def getTarget(self) -> Targets:
        return self.target

    def setTarget(self, target:Targets):
        self.target = target

    def isTarget(self, target:Targets):
        return self.target == target

    def isTargetAmp(self):
        return self.isTarget( LaunchCalc.Targets.AMP )
    
    def isTargetSpeaker(self):
        return self.isTarget( LaunchCalc.Targets.SPEAKER )

    def isTargetTrap(self):
        return ( 
            self.isTarget( LaunchCalc.Targets.TRAP1 ) or
            self.isTarget( LaunchCalc.Targets.TRAP2 ) or
            self.isTarget( LaunchCalc.Targets.TRAP3 )
        )

    def modifyAimAdjust(self, amount:float):
        self.aimAdjust.set( self.aimAdjust.get() + amount )

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

    def inRotationRange(self):
        range = 0.0
        match self.getTarget():
            case LaunchCalc.Targets.SPEAKER:
                range = self.speakerRotationRange.get()
            case LaunchCalc.Targets.AMP:
                range = self.ampRotationRange.get()
        return self.getRotationVariance() < range
    
    def inFarRange(self):
        range = 0.0
        match self.getTarget():
            case LaunchCalc.Targets.SPEAKER:
                range = self.speakerDistanceFar.get()
            case LaunchCalc.Targets.AMP:
                range = self.ampDistanceFar.get()
        return self.getDistance() < range
    
    def inNearRange(self):
        range = 0.0
        match self.getTarget():
            case LaunchCalc.Targets.SPEAKER:
                range = self.speakerDistanceNear.get()
            case LaunchCalc.Targets.AMP:
                range = self.ampRotationRange.get()
        return self.getDistance() < range
    
    def inAutoRange(self):
        range = 0.0
        match self.getTarget():
            case LaunchCalc.Targets.SPEAKER:
                range = self.speakerDistanceAuto.get()
            case LaunchCalc.Targets.AMP:
                range = self.ampDistanceAuto.get()
        return self.getDistance() < range

    def isAutoLaunchInRange(self) -> bool:
        return self.inRotationRange() and self.inAutoRange()
    
    def isAutoLaunchApproved(self) -> bool:
        return (
            self.autoLaunch.get() and
            self.isAutoLaunchInRange()
        )