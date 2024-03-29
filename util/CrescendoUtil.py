import math

from wpilib import DriverStation
from wpimath.geometry import Pose2d, Translation2d, Rotation2d

from .NTTunableFloat import NTTunableFloat

fieldWidth = NTTunableFloat( "Crescendo/FieldWidth", 8.31, persistent=True )
speakerTargetX = NTTunableFloat( "Crescendo/Speaker/X", 0.00, persistent=True )
speakerTargetY = NTTunableFloat( "Crescendo/Speaker/Y", 5.55, persistent=True )
speakerTargetH = NTTunableFloat( "Crescendo/Speaker/H", 2.0431, persistent=True )
robotPivotH = NTTunableFloat( "Crescendo/RobotPivot/H", 0.25, persistent=True )
ampTargetX = NTTunableFloat( "Crescendo/Amp/X", 1.80, persistent=True )
ampTargetY = NTTunableFloat( "Crescendo/Amp/Y", 7.90, persistent=True )
ampTargetH = NTTunableFloat( "Crescendo/Amp/H", 4.0, persistent=True )
ampTargetR = NTTunableFloat( "Crescendo/Amp/Rotation", -90.0, persistent=True)

class CrescendoUtil:
    @staticmethod
    def convertTranslationToRedAlliance(translation:Translation2d):
        x = translation.X()
        y = translation.Y()
        newY = fieldWidth.get() - y
        return Translation2d( x, newY )
    
    @staticmethod
    def convertPoseToRedAlliance(pose:Pose2d):
        newT = CrescendoUtil.convertTranslationToRedAlliance( pose.translation() )
        newR = pose.rotation().rotateBy( Rotation2d( math.pi ) )
        return Pose2d( newT, newR )
    
    @staticmethod
    def getSpeakerTarget():
        target = Translation2d( speakerTargetX.get(), speakerTargetY.get() )
        if DriverStation.getAlliance() == DriverStation.Alliance.kRed:
            target = CrescendoUtil.convertTranslationToRedAlliance( target )
        return target
    
    @staticmethod
    def getSpeakerPose():
        pose = Pose2d( CrescendoUtil.getSpeakerTarget(), Rotation2d(0) )
        return pose
    
    @staticmethod
    def getSpeakerHeight():
        return speakerTargetH.get()

    @staticmethod
    def getRobotPivotHeight():
        return robotPivotH.get()

    @staticmethod
    def getAmpTarget():
        target = Translation2d( ampTargetX.get(), ampTargetY.get() )
        if DriverStation.getAlliance() == DriverStation.Alliance.kRed:
            target = CrescendoUtil.convertTranslationToRedAlliance( target ) 

    @staticmethod
    def getAmpPose():
        pose = Pose2d(
            Translation2d( ampTargetX.get(), ampTargetY.get() ),
            Rotation2d(0).fromDegrees( ampTargetR.get() )
        )
        if DriverStation.getAlliance() == DriverStation.Alliance.kRed:
            pose = CrescendoUtil.convertPoseToRedAlliance( pose )
        return pose

    @staticmethod
    def getAmpHeight():
        return ampTargetH.get()

    @staticmethod
    def getStageTarget():
        return Translation2d(0,0)