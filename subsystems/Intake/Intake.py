from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import RobotState

from util import *
from .IntakeIO import IntakeIO

class Intake(Subsystem):
    class IntakeSpeeds:
        __priv__ = {
            0: NTTunableFloat( "/Config/Intake/Speeds/Load", 0.35 ),
            1: NTTunableFloat( "/Config/Intake/Speeds/Handoff", 0.50 ),
            2: NTTunableFloat( "/Config/Intake/Speeds/Eject", -1.0 ),
        }
        Stop = 0
        Load = __priv__[0].get()
        Handoff = __priv__[1].get()
        Eject = __priv__[2].get()

    def __init__(self, intake:IntakeIO):
        self.intake = intake
        self.intakeInputs = intake.IntakeIOInputs()
        self.intakeLogger = NetworkTableInstance.getDefault().getStructTopic( "/Intake", IntakeIO.IntakeIOInputs ).publish()

        self.offline = NTTunableBoolean( "/OfflineOverride/Intake", False )

    def periodic(self):
        # Logging
        self.intake.updateInputs( self.intakeInputs )
        self.intakeLogger.set( self.intakeInputs )

        # Run Subsystem
        if RobotState.isDisabled() or self.offline.get():
            self.stop()

        if False: #self.isCharacterizing.get():
            self.intake.runCharacterization( self.charSettingsVolts.get(), self.charSettingsRotation.get() )
        else:
            self.intake.run()

        # Post Run Logging
        #??? Don't Need It (Desired State / Current State)

    def set(self, speed:IntakeSpeeds):
        self.intake.setVelocity( speed )

    def stop(self) -> None:
        self.set( self.IntakeSpeeds.Stop )

    def setBrake(self, brake:bool) -> None:
        self.intake.setBrake(brake)

    def hasNote(self) -> bool:
        return False
    
    def isRunning(self) -> bool:
        return ( self.intake.getVelocity() != self.IntakeSpeeds.Stop )