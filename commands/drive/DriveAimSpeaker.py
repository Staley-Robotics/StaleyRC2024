import typing

from subsystems import SwerveDrive
from commands.drive.DriveByStick import DriveByStick
from util import CrescendoUtil

class DriveAimSpeaker(DriveByStick):
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
            holonomicX = lambda: self.target.X() - swerveDrive.getPose().X(),
            holonomicY = lambda: self.target.Y() - swerveDrive.getPose().Y(),
            rotate = lambda: 0.0
        )

        # Write New Name
        self.setName( "DriveAimSpeaker" )
        self.holdFieldRelative = False

    def initialize(self):
        # Update with existing Speaker Target (safe guard for load time alliance information)
        self.target = CrescendoUtil.getSpeakerTarget()
        
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