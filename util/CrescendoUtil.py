from wpimath.geometry import *

from .NTTunableFloat import *

fieldWidth = NTTunableFloat( "Crescendo/FieldWidth", 8.17, persistent=True)

class CrescendoUtil:
    @staticmethod
    def convertTranslationToRedAlliance(translation:Translation2d):
        x = translation.X()
        y = translation.Y()
        newY = fieldWidth.get() - y
        return Translation2d( x, newY )