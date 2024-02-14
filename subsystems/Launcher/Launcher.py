from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import RobotState

from .LauncherIO import LauncherIO
from util import *

class Launcher(Subsystem):
    class LauncherSpeeds:
        __priv__ = {
            0: NTTunableFloat( "/Config/LauncherSpeeds/Speaker/Left", 0.95 ),
            1: NTTunableFloat( "/Config/LauncherSpeeds/Speaker/Right", 0.85 ),
            2: NTTunableFloat( "/Config/LauncherSpeeds/Amp/Left", 0.30 ),
            3: NTTunableFloat( "/Config/LauncherSpeeds/Amp/Right", 0.20 ),
            4: NTTunableFloat( "/Config/LauncherSpeeds/Trap/Left", 0.50 ),
            5: NTTunableFloat( "/Config/LauncherSpeeds/Trap/Right", 0.40 ),
            6: NTTunableFloat( "/Config/LauncherSpeeds/Source/Left", -1.0 ),
            7: NTTunableFloat( "/Config/LauncherSpeeds/Source/Right", -1.0 ),
        }

        Stop = 0
        SpeakerLeft = __priv__[0].get()
        SpeakerRight = __priv__[1].get()
        AmpLeft = __priv__[2].get()
        AmpRight = __priv__[3].get()
        TrapLeft = __priv__[4].get()
        TrapRight = __priv__[5].get()
        SourceLeft = __priv__[6].get()
        SourceRight = __priv__[7].get()

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

    def set(self, leftSpeed, rightSpeed):
        self.launcher.setVelocity( leftSpeed, rightSpeed )

    def stop(self):
        self.set( self.LauncherSpeeds.Stop, self.LauncherSpeeds.Stop )

    # def speaker(self):
    #     self.set( self.LauncherSpeeds.SpeakerLeft, self.LauncherSpeeds.SpeakerRight )

    # def amp(self):
    #     self.set( self.LauncherSpeeds.AmpLeft, self.LauncherSpeeds.AmpRight )

    # def trap(self):
    #     self.set( self.LauncherSpeeds.TrapLeft, self.LauncherSpeeds.TrapRight )

    # def source(self):
    #     self.set( self.LauncherSpeeds.SourceLeft, self.LauncherSpeeds.SourceRight )

    def isRunning(self) -> bool:
        left, right = self.launcher.getVelocity()
        return ( left != self.LauncherSpeeds.Stop or right != self.LauncherSpeeds.Stop)

    def hasLaunched(self) -> bool:
        pass

    def atSpeed(self, errorRange:float = 0) -> bool:
        status = self.launcher.atSetpoint(errorRange)
        return ( status[0] and status[1] )