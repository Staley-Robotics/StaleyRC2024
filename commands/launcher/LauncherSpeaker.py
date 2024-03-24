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
class LauncherSpeaker(Command):
    def __init__( self,
                  launcher:Launcher,
                  getDistance:typing.Callable[[],float] = lambda: 0.0
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.launcher = launcher
        self.getDistance = getDistance

        self.setName( "LauncherSpeaker" )
        self.addRequirements( launcher )
        self.timer = Timer()

    def initialize(self) -> None:
        self.timer.reset()
        self.timer.start()

    def execute(self) -> None:
        if self.getDistance() < 4.0:
            self.launcher.set(Launcher.LauncherSpeeds.SpeakerLeftLow.get(), Launcher.LauncherSpeeds.SpeakerRightLow.get())
        # elif self.getDistance() < 5.0:
        #     self.launcher.set(Launcher.LauncherSpeeds.SpeakerLeftMedium.get(), Launcher.LauncherSpeeds.SpeakerLeftMedium.get())
        # elif self.getDistance() < 6.0:
        #     self.launcher.set(Launcher.LauncherSpeeds.SpeakerLeftHigh.get(), Launcher.LauncherSpeeds.SpeakerLeftHigh.get())
        else:
            self.launcher.set(Launcher.LauncherSpeeds.Stop.get(), Launcher.LauncherSpeeds.Stop.get())

    def end(self, interrupted:bool) -> None:
        self.launcher.set(Launcher.LauncherSpeeds.Stop.get(), Launcher.LauncherSpeeds.Stop.get())
        self.timer.stop()

    def isFinished(self) -> bool:
        return self.timer.hasElapsed( Launcher.LauncherSpeeds.TimeDelay.get() ) or self.launcher.hasLaunched()
    
    def runsWhenDisabled(self) -> bool: return False
