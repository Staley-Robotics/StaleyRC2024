from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import RobotState, Timer

from .LauncherIO import LauncherIO
from util import *

class Launcher(Subsystem):
    class LauncherSpeeds:
        SpeakerLeftHigh = NTTunableFloat( "/Config/LauncherSpeeds/Speaker/High/Left", 14500.0, persistent=True )
        SpeakerRightHigh = NTTunableFloat( "/Config/LauncherSpeeds/Speaker/High/Right", 12000.0, persistent=True )
        SpeakerLeftMedium = NTTunableFloat( "/Config/LauncherSpeeds/Speaker/Medium/Left", 14500.0, persistent=True )
        SpeakerRightMedium = NTTunableFloat( "/Config/LauncherSpeeds/Speaker/Medium/Right", 12000.0, persistent=True )
        SpeakerLeftLow = NTTunableFloat( "/Config/LauncherSpeeds/Speaker/Low/Left", 14500.0, persistent=True )
        SpeakerRightLow = NTTunableFloat( "/Config/LauncherSpeeds/Speaker/Low/Right", 12000.0, persistent=True )
        SpeakerDistanceHigh = NTTunableFloat( "/Config/LauncherSpeeds/Speaker/High/Distance", 5.0, persistent=True )
        SpeakerDistanceMedium = NTTunableFloat( "/Config/LauncherSpeeds/Speaker/Medium/Distance", 4.0, persistent=True )
        SpeakerDistanceLow = NTTunableFloat( "/Config/LauncherSpeeds/Speaker/Low/Distance", 3.0, persistent=True )
        
        AmpLeft = NTTunableFloat( "/Config/LauncherSpeeds/Amp/Left", 3000.0, persistent=True )
        AmpRight = NTTunableFloat( "/Config/LauncherSpeeds/Amp/Right", 3000.0, persistent=True )
        TrapLeft = NTTunableFloat( "/Config/LauncherSpeeds/Trap/Left", 8000.0, persistent=True )
        TrapRight = NTTunableFloat( "/Config/LauncherSpeeds/Trap/Right", 8000.0, persistent=True )
        SourceLeft = NTTunableFloat( "/Config/LauncherSpeeds/Source/Left", -8000.0, persistent=True )
        SourceRight = NTTunableFloat( "/Config/LauncherSpeeds/Source/Right", -8000.0, persistent=True )
        TossLeft = NTTunableFloat( "/Config/LauncherSpeeds/Toss/Left", 12000.0, persistent=True )
        TossRight = NTTunableFloat( "/Config/LauncherSpeeds/Toss/Right", 12000.0, persistent=True )

        TimeDelay = NTTunableFloat( "/Config/LauncherSpeeds/Other/TimeDelay", 20.00, persistent=True )
        Eject = NTTunableFloat( "/Config/LauncherSpeeds/Other/Eject", 2500.0, persistent=True )
        Stop = NTTunableFloat( "/Config/LauncherSpeeds/Other/Stop", 0.0, persistent=True )
        ErrorRange = NTTunableFloat( "/Config/LauncherSpeeds/Other/ErrorRange", 350.0, persistent=True )

    def __init__(self, launcher:LauncherIO):
        # Tunables
        self.detectSensor = NTTunableBoolean( "/Config/Launcher/LaunchDetection/A-Sensor", True, persistent=True )
        self.detectVeloc = NTTunableBoolean( "/Config/Launcher/LaunchDetection/B-Veloc", True, persistent=True )
        self.detectVelocCount = NTTunableInt( "/Config/Launcher/LaunchDetection/B-VelocCount", 2, persistent=True )
        self.detectTimer = NTTunableFloat( "/Config/Launcher/LaunchDetection/C-Timer", 30.0, persistent=True )
        self.autoDetectTimer = NTTunableFloat( "/Config/Launcher/LaunchDetection/C-Timer", 3.0, persistent=True )

        self.launcher = launcher
        self.launcherInputs = launcher.LauncherIOInputs
        self.launcherLogger = NetworkTableInstance.getDefault().getStructTopic( "/Launcher", LauncherIO.LauncherIOInputs ).publish()
        self.launcherMeasuredLogger = NetworkTableInstance.getDefault().getTable( "/Logging/Launcher" )

        self.offline = NTTunableBoolean( "/DisableSubsystem/Launcher", False, persistent=True )

        self.launchTimer = Timer()
        self.launchAtSpeedCount = 0
        self.launchDipDetected = False
        self.launchDetected = False

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
            
            if self.isRunning() and not self.launchDetected:
                self.launchTimer.start()

                if self.atSpeed():
                    self.launchAtSpeedCount += 1
                    if self.launchAtSpeedCount > self.detectVelocCount.get() and self.launchDipDetected:
                        self.launchDetected = True
                else:
                    if self.launchAtSpeedCount > self.detectVelocCount.get():
                        self.launchDipDetected = True
                    self.launchAtSpeedCount = 0
            else:
                self.launchAtSpeedCount = 0
                self.launchDipDetected = False
                self.launchDetected = False
                self.launchTimer.stop()
                self.launchTimer.reset()

        # Post Run Logging
        self.launcherMeasuredLogger.putNumberArray( "Setpoint", self.launcher.getSetpoint() )
        self.launcherMeasuredLogger.putNumberArray( "Measured", self.launcher.getVelocity() )
        
        self.launcherMeasuredLogger.putBoolean( "LaunchDetect/AtSpeed", self.atSpeed() )
        self.launcherMeasuredLogger.putNumber( "LaunchDetect/AtSpeedCount", self.launchAtSpeedCount )
        self.launcherMeasuredLogger.putBoolean( "LaunchDetect/DipDetected", self.launchDipDetected )
        self.launcherMeasuredLogger.putBoolean( "LaunchDetect/LaunchDetected", self.launchDetected )
        
        self.launcherMeasuredLogger.putBoolean( "LaunchDetect/SensorDetected", self.launcher.hasLaunched() )
        self.launcherMeasuredLogger.putNumber( "LaunchDetect/SensorCount", self.launcher.getSensorCount() )

    def set(self, leftSpeed:float, rightSpeed:float):
        self.launcher.setVelocity( leftSpeed, rightSpeed )

    def stop(self):
        self.set( Launcher.LauncherSpeeds.Stop.get(), Launcher.LauncherSpeeds.Stop.get() )

    def setBrake(self, brake:bool):
        self.launcher.setBrake( brake )

    def isRunning(self) -> bool:
        if self.getCurrentCommand() == None or self.getCurrentCommand().getName() == "LauncherWait":
            return False
        
        left, right = self.launcher.getVelocity()
        return ( left != Launcher.LauncherSpeeds.Stop.get() or right != Launcher.LauncherSpeeds.Stop.get())

    def hasLaunched(self) -> bool:
        if self.detectSensor.get() and self.launcher.hasLaunched():
            return True
        elif self.detectVeloc.get() and self.launchDetected:
            return True
        else:
            if not RobotBase.isAutonomous():
                return self.launchTimer.hasElapsed( self.detectTimer.get() )
            else:
                return self.launchTimer.hasElapsed( self.autoDetectTimer.get() )

    def atSpeed(self, errorRange:float = 250.00) -> bool:
        spL, spR = self.launcher.getSetpoint()
        if spL == 0.0 and spR == 0.0:
            return False
        
        status = self.launcher.atSetpoint(errorRange)
        return ( status[0] and status[1] )