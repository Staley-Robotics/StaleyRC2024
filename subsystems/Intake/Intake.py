from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import RobotState, RobotBase

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
        self.intakeMeasuredLogger = NetworkTableInstance.getDefault().getTable( "/Logging/Intake" )
        
        if RobotBase.isSimulation():
            self.simHasNote = NTTunableBoolean( "/Testing/Intake/HasNote", False, persistent=False )

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
        self.intakeMeasuredLogger.putNumberArray( "Setpoint", self.intake.getSetpoint() )
        self.intakeMeasuredLogger.putNumberArray( "Measured", self.intake.getVelocity() )
        
        self.intakeMeasuredLogger.putBoolean( "hasNote", self.hasNote() )
        self.intakeMeasuredLogger.putBoolean( "isRunning", self.isRunning() )
        self.intakeMeasuredLogger.putBoolean( "isWaiting", self.isWaiting() )

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
        if RobotBase.isSimulation():
            return self.intake.getSensorIsBroken() or self.simHasNote.get()
        else:
            return self.intake.getSensorIsBroken()
    
    def foundNote(self) -> bool:
        return self.intake.foundNote()
    
    def isRunning(self) -> bool:
        if self.getCurrentCommand() == None or self.getCurrentCommand().getName() == "IntakeWait":
            return False
        
        upper, lower = self.intake.getVelocity()
        return ( upper != Intake.IntakeSpeeds.Stop.get() or lower != Intake.IntakeSpeeds.Stop.get() )

    def isWaiting(self) -> bool:
        return (
            self.hasNote() and
            ( self.getCurrentCommand() == None or
            self.getCurrentCommand().getName() == "IntakeWait" )
        )

    def setHasNote(self, hasNote:bool) -> None:
        self.simHasNote.set( hasNote )
