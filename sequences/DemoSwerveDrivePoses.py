import commands2
from wpimath.geometry import Pose2d, Rotation2d

import commands
from subsystems import SwerveDrive

class DemoSwerveDrivePoses(commands2.SequentialCommandGroup):
    def __init__(self, drivetrain:SwerveDrive):
        super().__init__()

        self.addCommands( commands.DriveToPose( drivetrain, lambda: Pose2d( 2.9 , 4.1, Rotation2d(0) ) ) )
        self.addCommands( commands.DriveToPose( drivetrain, lambda: Pose2d( 5.85, 2.4, Rotation2d(0) ) ) )
        self.addCommands( commands.DriveToPose( drivetrain, lambda: Pose2d( 5.85, 5.8, Rotation2d(0) ) ) )
        self.addCommands( commands.DriveToPose( drivetrain, lambda: Pose2d( 2.9 , 4.1, Rotation2d(0) ) ) )
