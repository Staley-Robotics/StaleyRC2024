from wpilib import DriverStation
from wpimath.geometry import *

from .NTTunableFloat import *

fieldWidth = NTTunableFloat( "Crescendo/FieldWidth", 8.31, persistent=True )
speakerTargetX = NTTunableFloat( "Crescendo/Speaker/X", 0.00, persistent=True )
speakerTargetY = NTTunableFloat( "Crescendo/Speaker/Y", 5.55, persistent=True )
speakerTargetH = NTTunableFloat( "Crescendo/Speaker/H", 2.0431, persistent=True )
robotPivotH = NTTunableFloat( "Crescendo/RobotPivot/H", 0.25, persistent=True )

class CrescendoUtil:
    @staticmethod
    def convertTranslationToRedAlliance(translation:Translation2d):
        x = translation.X()
        y = translation.Y()
        newY = fieldWidth.get() - y
        return Translation2d( x, newY )
    
    @staticmethod
    def getSpeakerTarget():
        target = Translation2d( speakerTargetX.get(), speakerTargetY.get() )
        if DriverStation.getAlliance() == DriverStation.Alliance.kRed:
            target = CrescendoUtil.convertTranslationToRedAlliance( target )
        return target
    
    @staticmethod
    def getSpeakerHeight():
        return speakerTargetH.get()

    @staticmethod
    def getRobotPivotHeight():
        return robotPivotH.get()

    @staticmethod
    def getAmpTarget():
        return Translation2d(0,0)
    
    @staticmethod
    def getStageTarget():
        return Translation2d(0,0)