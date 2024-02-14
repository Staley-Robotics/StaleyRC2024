from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import RobotState

from .LauncherIO import LauncherIO
from util import *

class Launcher(Subsystem):
    class LauncherSpeeds:
        __priv__ = {
            0: NTTunableFloat( "/Config/Launcher/Speeds/LeftLaunch", 0.95 ),
            1: NTTunableFloat( "/Config/Launcher/Speeds/RightLaunch", 0.85 ),
            2: NTTunableFloat( "/Config/Launcher/Speeds/LeftReceive", -1.0 ),
            3: NTTunableFloat( "/Config/Launcher/Speeds/RightReceive", -1.0 ),
        }

        Stop = 0
        LeftLaunch = __priv__[0].get()
        RightLaunch = __priv__[1].get()
        LeftReceive = __priv__[2].get()
        RightReceive = __priv__[3].get()

    def __init__(self, launcher:LauncherIO):
        self.launcher = launcher
        self.launcherInputs = launcher.LauncherIOInputs
        self.launcherLogger = NetworkTableInstance.getDefault().getStructTopic( "/Launcher", LauncherIO.LauncherIOInputs ).publish()

        self.offline = NTTunableBoolean( "/OfflineOverride/Launcher", False )

    def periodic(self):
        # Logging
        self.launcher.updateInputs( self.launcherInputs )
        self.launcherLogger.set( self.launcherInputs )

        # Run Subsystem
        if RobotState.isDisabled() or self.offline.get():
            self.stop()

        if False: #self.isCharacterizing.get():
            self.intake.runCharacterization( self.charSettingsVolts.get(), self.charSettingsRotation.get() )
        else:
            self.launcher.run()

        # Post Run Logging
        #??? Don't Need It (Desired State / Current State)

    def stop(self):
        self.launcher.setVelocity( self.LauncherSpeeds.Stop, self.LauncherSpeeds.Stop )

    def launch(self):
        self.launcher.setVelocity( self.LauncherSpeeds.LeftLaunch, self.LauncherSpeeds.RightLaunch )

    def receive(self):
        self.launcher.setVelocity( self.LauncherSpeeds.LeftReceive, self.LauncherSpeeds.RightReceive )

    def isRunning(self) -> bool:
        left, right = self.launcher.getVelocity()
        return ( left != self.LauncherSpeeds.Stop or right != self.LauncherSpeeds.Stop)

    def hasLaunched(self) -> bool:
        pass

    def atSpeed(self) -> bool:
        leftVeloc, rightVeloc = self.launcher.getVelocity()
        leftSp, rightSp = self.launcher.getSetpoint()
        return ( leftVeloc == leftSp and rightVeloc == rightSp )