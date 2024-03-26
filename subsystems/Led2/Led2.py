from commands2 import Subsystem
from wpilib import Color, DriverStation, RobotState, RobotBase

from .Led2IO import Led2IO
from util import NTTunableBoolean

class Led2(Subsystem):
    def __init__(self, led:Led2IO):
        # NT Tunables
        self.offline = NTTunableBoolean( "/DisableSubsystem/LED", False, persistent=True )

        # Global Variables
        self.led = led
        self.allianceColor = Color.kBlack
        self.allianceColorDark = Color.kBlack

    def periodic(self):
        # Logger

        # Update Alliance Color
        self.updateAllianceColor()
        
        # Offline State
        if self.offline.get():
            self.led.solid( Color.kBlack )
        else:
            self.determineState()

        # Run LEDs
        self.led.run()

    def updateAllianceColor(self):
        match DriverStation.getAlliance():
            case DriverStation.Alliance.kBlue:
                self.allianceColor = Color.kBlue
                self.allianceColorDark = Color.kDarkBlue
            case DriverStation.Alliance.kRed:
                self.allianceColor = Color.kRed
                self.allianceColorDark = Color.kDarkRed
            case _:
                self.allianceColor = Color.kLightYellow
                self.allianceColorDark = Color.kYellow

    def determineState(self):
        # Determine State
        if RobotState.isEStopped():
            self.led.strobe( [Color.kDarkRed], 0.5 )
        elif RobotState.isDisabled():
            self.led.solid( self.allianceColor )
        elif RobotState.isAutonomous():
            self.led.wave( self.allianceColor, self.allianceColorDark, 20.0, 1.0 )
        elif RobotState.isTeleop():
            pass
        else:
            self.led.solid( Color.kHoneydew )
            