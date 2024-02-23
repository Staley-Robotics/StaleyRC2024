### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems import Launcher
from util import *

# Intake Load Command
class LauncherSpeaker(Command):
    def __init__( self,
                  launcher:Launcher,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.launcher = launcher

        self.setName( "LauncherSpeaker" )
        self.addRequirements( launcher )

    def initialize(self) -> None: pass

    def execute(self) -> None:
        self.launcher.set(Launcher.LauncherSpeeds.SpeakerLeft.get(), Launcher.LauncherSpeeds.SpeakerRight.get())

    def end(self, interrupted:bool) -> None:
        self.launcher.set(Launcher.LauncherSpeeds.Stop.get(), Launcher.LauncherSpeeds.Stop.get())

    def isFinished(self) -> bool:
        return False
        return self.launcher.hasLaunched()
    
    def runsWhenDisabled(self) -> bool: return False
