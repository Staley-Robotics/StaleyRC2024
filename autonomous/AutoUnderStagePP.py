import typing

from commands2 import SequentialCommandGroup
from wpimath.geometry import *
from wpimath.trajectory import *
from wpimath.trajectory.constraint import *

from subsystems import SwerveDrive
from commands import DrivePathPP

class AutoUnderStagePP(SequentialCommandGroup):
    def __init__(self, swerveDrive:SwerveDrive):
        super().__init__()
        self.setName("AutoUnderStage")
        self.addRequirements( swerveDrive )

        self.swerveDrive = swerveDrive
        self.addCommands( DrivePathPP(swerveDrive, self.getWaypoints, lambda: Rotation2d(0).fromDegrees(90)) )

    def initialize(self):
        # Set Linear Velocity?
        super().initialize()
        pass

    def getWaypoints(self) -> typing.List[Pose2d]:
        return [
            self.swerveDrive.getPose(),
            Pose2d( Translation2d( 4.3, 3.1 ), Rotation2d(0).fromDegrees(30) ),
            Pose2d( Translation2d( 5.8, 4.2 ), Rotation2d(0).fromDegrees(0) ),
            Pose2d( Translation2d( 7.5, 4.2 ), Rotation2d(0).fromDegrees(0) )
        ]