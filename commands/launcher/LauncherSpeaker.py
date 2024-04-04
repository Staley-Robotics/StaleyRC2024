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

    def initialize(self) -> None:
        pass

    def execute(self) -> None:
        if self.getDistance() < Launcher.LauncherSpeeds.SpeakerDistanceLow.get():
            self.launcher.set(Launcher.LauncherSpeeds.SpeakerLeftLow.get(), Launcher.LauncherSpeeds.SpeakerRightLow.get())
        elif self.getDistance() < Launcher.LauncherSpeeds.SpeakerDistanceMedium.get():
            self.launcher.set(Launcher.LauncherSpeeds.SpeakerLeftMedium.get(), Launcher.LauncherSpeeds.SpeakerLeftMedium.get())
        # elif self.getDistance() < Launcher.LauncherSpeeds.SpeakerDistanceHigh.get():
        #     self.launcher.set(Launcher.LauncherSpeeds.SpeakerLeftHigh.get(), Launcher.LauncherSpeeds.SpeakerLeftHigh.get())
        else: 
            # self.launcher.set(Launcher.LauncherSpeeds.Stop.get(), Launcher.LauncherSpeeds.Stop.get())
            self.launcher.set(Launcher.LauncherSpeeds.SpeakerLeftHigh.get(), Launcher.LauncherSpeeds.SpeakerLeftHigh.get())


    def end(self, interrupted:bool) -> None:
        if not RobotState.isAutonomous():
            self.launcher.set(Launcher.LauncherSpeeds.Stop.get(), Launcher.LauncherSpeeds.Stop.get())

    def isFinished(self) -> bool:
        return self.launcher.hasLaunched()
    
    def runsWhenDisabled(self) -> bool: return False
