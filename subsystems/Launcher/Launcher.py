from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import RobotState

from .LauncherIO import LauncherIO
from util import *

class Launcher(Subsystem):
    class LauncherSpeeds:
        DeleteStop = NTTunableFloat( "/Config/LauncherSpeeds/Stop", 0.0, persistent=False ) ## Safe to Delete after several load times
        
        SpeakerLeft = NTTunableFloat( "/Config/LauncherSpeeds/Speaker/Left", 12000.0, persistent=True )
        SpeakerRight = NTTunableFloat( "/Config/LauncherSpeeds/Speaker/Right", 10000.0, persistent=True )
        AmpLeft = NTTunableFloat( "/Config/LauncherSpeeds/Amp/Left", 2000.0, persistent=True )
        AmpRight = NTTunableFloat( "/Config/LauncherSpeeds/Amp/Right", 2000.0, persistent=True )
        TrapLeft = NTTunableFloat( "/Config/LauncherSpeeds/Trap/Left", 8000.0, persistent=True )
        TrapRight = NTTunableFloat( "/Config/LauncherSpeeds/Trap/Right", 8000.0, persistent=True )
        SourceLeft = NTTunableFloat( "/Config/LauncherSpeeds/Source/Left", -8000.0, persistent=True )
        SourceRight = NTTunableFloat( "/Config/LauncherSpeeds/Source/Right", -8000.0, persistent=True )
        
        Eject = NTTunableFloat( "/Config/LauncherSpeeds/Other/Eject", 1000.0, persistent=True )
        Stop = NTTunableFloat( "/Config/LauncherSpeeds/Other/Stop", 0.0, persistent=True )
        ErrorRange = NTTunableFloat( "/Config/LauncherSpeeds/Other/ErrorRange", 100.0, persistent=True )

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
        self.launcherMeasuredLogger.putNumber( "SensorCount", self.launcher.getSensorCount() )

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

    def atSpeed(self, errorRange:float = 100.00) -> bool:
        status = self.launcher.atSetpoint(errorRange)
        return ( status[0] and status[1] )