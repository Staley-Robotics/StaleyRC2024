# Import Python

# Import FRC
from commands2 import InstantCommand
from wpilib import RobotState

# Import Subsystems and Commands
from subsystems import SwerveDrive
from util import *
# Constants


# Toggle: Half Speed
class ToggleHalfSpeed(InstantCommand):
    finetuneEnabled = NTTunableBoolean( "/CmdConfig/DriveByStick/Control/FineEnabled", False )

    def __init__(self, DriveSubsystem:SwerveDrive) -> None:
        super().__init__(
            toRun=lambda: self.finetuneEnabled.set( not self.finetuneEnabled.get() )
        )

    def runsWhenDisabled(self) -> bool: return True

# Toggle: Field Relative
class ToggleFieldRelative(InstantCommand):
    def __init__(self, DriveSubsystem:SwerveDrive) -> None:
        super().__init__(
            toRun=lambda: DriveSubsystem.fieldRelative.set( not DriveSubsystem.fieldRelative.get() )
        )
    
    def runsWhenDisabled(self) -> bool: return True
