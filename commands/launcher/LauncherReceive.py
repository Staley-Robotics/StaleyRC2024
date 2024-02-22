### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems import Launcher
from util import *

# Intake Load Command
class LauncherReceive(Command):
    def __init__( self,
                  launcher:Launcher,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.launcher = launcher

        self.setName( "LauncherReceive" )
        self.addRequirements( launcher )

    def initialize(self) -> None: pass

    def execute(self) -> None:
        self.launcher.set(Launcher.LauncherSpeeds.SourceLeft.get(), Launcher.LauncherSpeeds.SourceRight.get())

    def end(self, interrupted:bool) -> None:
        self.launcher.set(Launcher.LauncherSpeeds.Stop.get(), Launcher.LauncherSpeeds.Stop.get())

    def isFinished(self) -> bool:
        return not self.launcher.hasLaunched()
    
    def runsWhenDisabled(self) -> bool: return False
