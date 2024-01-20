# Import Python
import math

# Import FRC
from commands2 import Command
from wpimath.kinematics import SwerveModuleState

# Import Subsystems and Commands
from subsystems import *

# Constants


class DriveLockdown(Command):
    def __init__(self, swerveDrive:SwerveDrive):
        super().__init__()
        self.setName( "DriveLockdown" )

        self.swerveDrive = swerveDrive
        self.addRequirements( [self.swerveDrive] )

    def execute(self):
        modStates = []
        for module in self.swerveDrive.modules:
            modStates.append(
                SwerveModuleState( 0, module.getReferencePosition().angle())
            )
        self.swerveDrive.runSwerveModuleStates( modStates )

    def end(self, interrupted:bool) -> None:
        pass

    def isFinished(self) -> bool:
        return False

