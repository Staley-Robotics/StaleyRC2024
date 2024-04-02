### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command
from wpilib import Timer

# Our Imports
from subsystems import Launcher
from util import *

# Intake Load Command
class LauncherToss(Command):
    def __init__( self,
                  launcher:Launcher,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.launcher = launcher

        self.setName( "LauncherToss" )
        self.addRequirements( launcher )
        self.timer = Timer()

    def initialize(self) -> None:
        self.timer.reset()
        self.timer.start()

    def execute(self) -> None:
        self.launcher.set(Launcher.LauncherSpeeds.TossLeft.get(), Launcher.LauncherSpeeds.TossRight.get())

    def end(self, interrupted:bool) -> None:
        self.timer.stop()
        if not interrupted:
            self.launcher.set(Launcher.LauncherSpeeds.Stop.get(), Launcher.LauncherSpeeds.Stop.get())
        

    def isFinished(self) -> bool:
        return self.timer.hasElapsed( Launcher.LauncherSpeeds.TimeDelay.get() ) or self.launcher.hasLaunched()
    
    def runsWhenDisabled(self) -> bool: return False
