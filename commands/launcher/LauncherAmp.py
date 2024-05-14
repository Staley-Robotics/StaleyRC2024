### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command
from wpilib import RobotState

# Our Imports
from subsystems import Launcher
from util import *

# Intake Load Command
class LauncherAmp(Command):
    def __init__( self,
                  launcher:Launcher,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.launcher = launcher

        self.setName( "LauncherAmp" )
        self.addRequirements( launcher )

    def initialize(self) -> None: pass

    def execute(self) -> None:
        self.launcher.set(Launcher.LauncherSpeeds.AmpLeft.get(), Launcher.LauncherSpeeds.AmpRight.get())

    def end(self, interrupted:bool) -> None:
        if not RobotState.isAutonomous():
            self.launcher.set(Launcher.LauncherSpeeds.Stop.get(), Launcher.LauncherSpeeds.Stop.get())

    def isFinished(self) -> bool:
        return self.launcher.hasLaunched()
    
    def runsWhenDisabled(self) -> bool: return False
