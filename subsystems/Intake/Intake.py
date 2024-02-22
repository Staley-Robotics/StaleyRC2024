from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import RobotState

from util import *
from .IntakeIO import IntakeIO

class Intake(Subsystem):
    class IntakeSpeeds:
        #__priv__ = {
        #    0: NTTunableFloat( "/Config/IntakeSpeeds/Load", 0.35, persistent=True ),
        #    1: NTTunableFloat( "/Config/IntakeSpeeds/Handoff", 0.50, persistent=True ),
        #    2: NTTunableFloat( "/Config/IntakeSpeeds/Eject", -1.0, persistent=True ),
        #}
        Stop = NTTunableFloat( "/Config/IntakeSpeeds/Stop", 0.0, persistent=True )
        Load = NTTunableFloat( "/Config/IntakeSpeeds/Load", 0.35, persistent=True )
        Handoff = NTTunableFloat( "/Config/IntakeSpeeds/Handoff", 0.50, persistent=True )
        Eject = NTTunableFloat( "/Config/IntakeSpeeds/Eject", -1.0, persistent=True )

    def __init__( self, intake:IntakeIO ):
        self.intake = intake
        self.intakeInputs = intake.IntakeIOInputs()
        self.intakeLogger = NetworkTableInstance.getDefault().getStructTopic( "/Intake", IntakeIO.IntakeIOInputs ).publish()

        self.offline = NTTunableBoolean( "/DisableSubsystem/Intake", False, persistent=True )

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

    def set(self, speed:float):
        self.intake.setVelocity( speed, speed )

    def stop(self) -> None:
        self.set( Intake.IntakeSpeeds.Stop.get() )

    # def load(self):
    #     self.set( self.IntakeSpeeds.Load )

    # def handoff(self):
    #     self.set( self.IntakeSpeeds.Handoff )

    # def eject(self):
    #     self.set( self.IntakeSpeeds.Eject )

    def setBrake(self, brake:bool) -> None:
        self.intake.setBrake( brake )

    def hasNote(self) -> bool:
        return False
    
    def isRunning(self) -> bool:
        upper, lower = self.intake.getVelocity()
        return ( upper != Intake.IntakeSpeeds.Stop.get() or lower != Intake.IntakeSpeeds.Stop.get() )
