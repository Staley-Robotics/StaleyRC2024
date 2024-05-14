### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command
from wpilib import RobotState

# Our Imports
from commands.launcher.LauncherSpeaker import LauncherSpeaker
from subsystems import Launcher
from util import *

# Intake Load Command
class LauncherSpeakerAuto(LauncherSpeaker):
    def __init__( self,
                  launcher:Launcher,
                  getDistance:typing.Callable[[],float] = lambda: 0.0
                ):
        # CommandBase Initiation Configurations
        super().__init__(
            launcher,
            getDistance
        )

        self.setName( "LauncherSpeakerAuto" )

    def isFinished(self) -> bool:
        return not RobotState.isAutonomous()
    
    def runsWhenDisabled(self) -> bool: return False
