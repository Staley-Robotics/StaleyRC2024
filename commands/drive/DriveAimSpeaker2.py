import typing

from wpimath.geometry import Rotation2d

from subsystems import SwerveDrive
from commands.drive.DriveByStick import DriveByStick
from util import CrescendoUtil

class DriveAimSpeaker2(DriveByStick):
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
            holonomicX = lambda: 0.0, # self.target.X() - swerveDrive.getPose().X(),
            holonomicY = lambda: 0.0, #self.target.Y() - swerveDrive.getPose().Y(),
            rotate = self.rotate
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

    def rotate(self) -> float:
        hX = self.target.X() - self.drive.getPose().X()
        hY = self.target.Y() - self.drive.getPose().Y()
        robotAngle:float = self.drive.getRobotAngle().radians()
        goalAngle:float = Rotation2d( x=-hX, y=-hY ).radians()
        rTarget = self.tPid.calculate(robotAngle, goalAngle)
        #rTarget *= 100
        print( rTarget )
        return rTarget

    def end(self, interrupted:bool):
        # Reset Field Relative
        self.isFieldRelative.set( self.holdFieldRelative )

        # End DriveByStick
        super().end(interrupted)