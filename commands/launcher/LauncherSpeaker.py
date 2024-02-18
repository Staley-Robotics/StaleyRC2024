### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems.Launcher import Launcher
from util import *

# Intake Load Command
class LauncherSpeaker(Command):
    def __init__( self,
                  launcher:Launcher,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.launcher = launcher

    def initialize(self) -> None: pass

    def execute(self) -> None:
        self.launcher.set(Launcher.LauncherSpeeds.SpeakerLeft, Launcher.LauncherSpeeds.SpeakerRight)

    def end(self, interrupted:bool) -> None:
        self.launcher.set(Launcher.LauncherSpeeds.Stop, Launcher.LauncherSpeeds.Stop)

    def isFinished(self) -> bool:
        return self.launcher.hasLaunched()
    
    def runsWhenDisabled(self) -> bool: return False
