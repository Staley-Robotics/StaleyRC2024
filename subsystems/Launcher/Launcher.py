from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import RobotState

from .LauncherIO import LauncherIO
from util import *

class Launcher(Subsystem):
    class LauncherSpeeds:
        Stop = NTTunableFloat( "/Config/LauncherSpeeds/Stop", 0.0, persistent=True )
        SpeakerLeft = NTTunableFloat( "/Config/LauncherSpeeds/Speaker/Left", 0.95, persistent=True )
        SpeakerRight = NTTunableFloat( "/Config/LauncherSpeeds/Speaker/Right", 0.85, persistent=True )
        AmpLeft = NTTunableFloat( "/Config/LauncherSpeeds/Amp/Left", 0.30, persistent=True )
        AmpRight = NTTunableFloat( "/Config/LauncherSpeeds/Amp/Right", 0.20, persistent=True )
        TrapLeft = NTTunableFloat( "/Config/LauncherSpeeds/Trap/Left", 0.50, persistent=True )
        TrapRight = NTTunableFloat( "/Config/LauncherSpeeds/Trap/Right", 0.40, persistent=True )
        SourceLeft = NTTunableFloat( "/Config/LauncherSpeeds/Source/Left", -1.0, persistent=True )
        SourceRight = NTTunableFloat( "/Config/LauncherSpeeds/Source/Right", -1.0, persistent=True )

    def __init__(self, launcher:LauncherIO):
        self.launcher = launcher
        self.launcherInputs = launcher.LauncherIOInputs
        self.launcherLogger = NetworkTableInstance.getDefault().getStructTopic( "/Launcher", LauncherIO.LauncherIOInputs ).publish()
        self.launcherMeasuredLogger = NetworkTableInstance.getDefault().getTable( "/Logging/Launcher" )

        self.offline = NTTunableBoolean( "/DisableSubsystem/Launcher", False, persistent=True )

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
        self.launcherMeasuredLogger.putNumberArray( "Setpoint", self.launcher.getSetpoint() )
        self.launcherMeasuredLogger.putNumberArray( "Measured", self.launcher.getVelocity() )

    def set(self, leftSpeed:float, rightSpeed:float):
        self.launcher.setVelocity( leftSpeed, rightSpeed )

    def stop(self):
        self.set( Launcher.LauncherSpeeds.Stop.get(), Launcher.LauncherSpeeds.Stop.get() )

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
        return ( left != Launcher.LauncherSpeeds.Stop.get() or right != Launcher.LauncherSpeeds.Stop.get())

    def hasLaunched(self) -> bool:
        return self.launcher.hasLaunched()

    def atSpeed(self, errorRange:float = 0) -> bool:
        status = self.launcher.atSetpoint(errorRange)
        print( status )
        return ( status[0] and status[1] )