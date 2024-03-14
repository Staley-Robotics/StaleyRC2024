import typing

from wpilib import DriverStation

from subsystems import SwerveDrive
from commands.drive.DriveByStick import DriveByStick
from util import CrescendoUtil

class DriveAimAmp(DriveByStick):
    def __init__( self,
                  swerveDrive:SwerveDrive,
                  velocityX:typing.Callable[[], float],
                  velocityY:typing.Callable[[], float],):
        # Get Target
        self.target = CrescendoUtil.getSpeakerTarget()

        # Initialize DriveByStick
        super().__init__( swerveDrive,
            velocityX = velocityX,
            velocityY = velocityY,
            holonomicX = self.getHolonomicX,
            holonomicY = lambda: 0,
            rotate = lambda: 0.0
        )

        # Write New Name
        self.setName( "DriveAimAmp" )
        self.holdFieldRelative = False

    def getHolonomicX(self) -> float:
        returnMe = 0

        if DriverStation.getAlliance() == DriverStation.Alliance.kRed:
            returnMe = -1.0
        elif DriverStation.getAlliance() == DriverStation.Alliance.kBlue:
            returnMe = 1.0
        else:
            returnMe = 0

        return returnMe

    def initialize(self):
        # Force Field Relative
        self.holdFieldRelative = self.isFieldRelative.get()
        self.isFieldRelative.set( True )

        # Initialize DriveByStick
        super().initialize()

    def end(self, interrupted:bool):
        # Reset Field Relative
        self.isFieldRelative.set( self.holdFieldRelative )

        # End DriveByStick
        super().end(interrupted)