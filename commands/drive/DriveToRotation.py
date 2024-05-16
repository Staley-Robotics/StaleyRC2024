import typing

from wpimath.geometry import Rotation2d

from subsystems import SwerveDrive
from commands.drive.DriveByStick import DriveByStick
from util import CrescendoUtil

class DriveToRotation(DriveByStick):
    def __init__( self,
                  swerveDrive:SwerveDrive,
                  velocityX:typing.Callable[[], float],
                  velocityY:typing.Callable[[], float],
                  rotation:typing.Callable[[], Rotation2d]
                  ):
        # Get Target Rotation
        self.getRotation = rotation

        # Initialize DriveByStick
        super().__init__( swerveDrive,
            velocityX = velocityX,
            velocityY = velocityY,
            rotate = self.rotate
        )

        # Write New Name
        self.setName( "DriveToRotation" )
        self.holdFieldRelative = False

    def initialize(self):
        # Force Field Relative
        self.holdFieldRelative = self.isFieldRelative.get()
        self.isFieldRelative.set( True )

        # Initialize DriveByStick
        super().initialize()

    def rotate(self) -> float:
        goalAngle:float = self.getRotation().radians()
        robotAngle:float = self.drive.getRobotAngle().radians()
        rTarget = self.tPid.calculate(robotAngle, goalAngle)
        return rTarget

    def end(self, interrupted:bool):
        # Reset Field Relative
        self.isFieldRelative.set( self.holdFieldRelative )

        # End DriveByStick
        super().end(interrupted)