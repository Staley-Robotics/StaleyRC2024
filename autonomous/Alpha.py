import typing

from commands2 import SequentialCommandGroup, ParallelCommandGroup
from wpimath.geometry import *
from wpimath.trajectory import *
from wpimath.trajectory.constraint import *

from subsystems import SwerveDrive,Intake,Indexer,Launcher,Pivot,Elevator
from sequences import NoteLoadGround
from commands import DrivePathPP

class Alpha(SequentialCommandGroup):
    def __init__( self,
                  swerveDrive:SwerveDrive, 
                  intake:Intake,
                  indexer:Indexer,
                  launcher:Launcher,
                  pivot:Pivot,
                  elevator:Elevator
                ):
        super().__init__()
        self.setName("AutoAlpha")
        self.addRequirements( swerveDrive, intake, indexer, launcher, pivot, elevator )

        self.swerveDrive = swerveDrive
        self.addCommands(
            ParallelCommandGroup(
                DrivePathPP(swerveDrive, self.getWaypoints, lambda: Rotation2d(0).fromDegrees(0)),
                #NoteLoadGround( intake, indexer, pivot, elevator)
            )
        )

    def initialize(self):
        # Set Linear Velocity?
        super().initialize()
        pass

    def getWaypoints(self) -> typing.List[Pose2d]:
        start = Pose2d( self.swerveDrive.getPose().translation(), Rotation2d(0) )
        possibleFinals = [
            Pose2d( Translation2d( 4.0, 7.0 ), Rotation2d(0) ),
            Pose2d( Translation2d( 4.0, 1.5 ), Rotation2d(0) )
        ]
        final = start.nearest( possibleFinals )

        return [
            self.swerveDrive.getPose(),
            final
        ]