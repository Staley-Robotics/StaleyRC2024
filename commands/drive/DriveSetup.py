# Import Python

# Import FRC
from commands2 import InstantCommand
from wpilib import RobotState

# Import Subsystems and Commands
from subsystems import SwerveDrive
from util import *
# Constants

# Toggle: Turbo
class ToggleTurboOn(InstantCommand):
    turbo = NTTunableBoolean( "/Driver1/isTurbo", False )

    def __init__(self) -> None:
        super().__init__(
            toRun=lambda: self.turbo.set( True )
        )

    def runsWhenDisabled(self) -> bool: return True

class ToggleTurboOff(InstantCommand):
    turbo = NTTunableBoolean( "/Driver1/isTurbo", False )

    def __init__(self) -> None:
        super().__init__(
            toRun=lambda: self.turbo.set( False )
        )

    def runsWhenDisabled(self) -> bool: return True

# Toggle: Half Speed
class ToggleHalfSpeed(InstantCommand):
    halfSpeed = NTTunableBoolean( "/Driver1/isHalfSpeed", False )

    def __init__(self) -> None:
        super().__init__(
            toRun=lambda: self.halfSpeed.set( not self.halfSpeed.get() )
        )

    def runsWhenDisabled(self) -> bool: return True

# Toggle: Field Relative
class ToggleFieldRelative(InstantCommand):
    fieldRelative = NTTunableBoolean( "/Driver1/isFieldRelative", True )

    def __init__(self) -> None:
        super().__init__(
            toRun=lambda: self.fieldRelative.set( not self.fieldRelative.get() )
        )
    
    def runsWhenDisabled(self) -> bool: return True
