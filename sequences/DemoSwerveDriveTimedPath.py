import commands2

import commands
from subsystems import SwerveDrive

class DemoSwerveDriveTimedPath(commands2.SequentialCommandGroup):
    def __init__(self, drivetrain:SwerveDrive):
        super().__init__()

        self.addCommands( commands.DriveForTime( drivetrain,  1,  0, 0, 2.0, True ) )
        self.addCommands( commands.DriveForTime( drivetrain,  0,  1, 0, 2.0, True ) )
        self.addCommands( commands.DriveForTime( drivetrain, -1,  0, 0, 1.0, True ) )
        self.addCommands( commands.DriveForTime( drivetrain,  0, -1, 0, 1.0, True ) )
        self.addCommands( commands.DriveForTime( drivetrain, -1,  0, 0, 1.0, True ) )
        self.addCommands( commands.DriveForTime( drivetrain,  0, -1, 0, 1.0, True ) )
        self.addCommands( commands.DriveForTime( drivetrain,  1,  1, 0, 1.5, True ) )
        self.addCommands( commands.DriveForTime( drivetrain, -1,  1, 0, 1.5, True ) )
