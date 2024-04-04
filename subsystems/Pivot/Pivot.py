from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import RobotState

from util import *
from .PivotIO import PivotIO

class Pivot(Subsystem):
    class PivotPositions:
        Upward = NTTunableFloat( "/Config/PivotPositions/Upward", 55.041, persistent=True )
        Speaker = NTTunableFloat( "/Config/PivotPositions/Speaker", 50.000, persistent=True )
        Handoff = NTTunableFloat( "/Config/PivotPositions/Handoff", 32.168, persistent=True )
        Amp = NTTunableFloat( "/Config/PivotPositions/Amp", 52.0, persistent=True )
        Trap = NTTunableFloat( "/Config/PivotPositions/Trap", -45.0, persistent=True )
        Source = NTTunableFloat( "/Config/PivotPositions/Source", -45.0, persistent=True )
        Downward = NTTunableFloat( "/Config/PivotPositions/Downward", -52.031, persistent=True )
        Toss = NTTunableFloat( "/Config/PivotPositions/Toss", 45.0, persistent=True )
        Eject = NTTunableFloat( "/Config/PivotPositions/Eject", 32.168, persistent=True )

    def __init__(self, pivot:PivotIO):
        self.pivot = pivot
        self.pivotInputs = pivot.PivotIOInputs
        self.pivotLogger = NetworkTableInstance.getDefault().getStructTopic( "/Pivot", PivotIO.PivotIOInputs ).publish()
        self.pivotMeasuredLogger = NetworkTableInstance.getDefault().getTable("/Logging/Pivot")
        
        self.offline = NTTunableBoolean( "/DisableSubsystem/Pivot", False, persistent=True )

    def periodic(self):
        # Logging
        self.pivot.updateInputs( self.pivotInputs )
        self.pivotLogger.set( self.pivotInputs )

        # Run Subsystem
        if RobotState.isDisabled() or self.offline.get():
            self.stop()

        if False: #self.isCharacterizing.get():
            self.pivot.runCharacterization( self.charSettingsVolts.get(), self.charSettingsRotation.get() )
        else:
            self.pivot.run()
            # self.pivot.pivotMotor.set(0)

        # Post Run Logging
        self.pivotMeasuredLogger.putNumber( "Setpoint", self.pivot.getSetpoint() )
        self.pivotMeasuredLogger.putNumber( "Measured", self.pivot.getPosition() )
            
    def set(self, position:float):
        pos = min(max(position, Pivot.PivotPositions.Downward.get()), Pivot.PivotPositions.Upward.get())
        self.pivot.setPosition( pos )

    def get(self):
        return self.pivot.getPosition()

    def stop(self):
        self.set( self.pivot.getPosition() )

    def atSetpoint(self, errorRange:float = 0.5) -> bool:
        return self.pivot.atSetpoint( errorRange )

    def atPosition(self, position:float) -> bool:
        if self.pivot.getSetpoint() == position:
            return self.atSetpoint()
        else:
            return False

    def atPositionSpeaker(self) -> bool:
        return self.atPosition( Pivot.PivotPositions.Speaker.get() )
    
    def atPositionHandoff(self) -> bool: 
        return self.atPosition( Pivot.PivotPositions.Handoff.get() )

    def atPositionAmp(self) -> bool: 
        return self.atPosition( Pivot.PivotPositions.Amp.get() )

    def atPositionTrap(self) -> bool: 
        return self.atPosition( Pivot.PivotPositions.Trap.get() )

    def atPositionSource(self) -> bool: 
        return self.atPosition( Pivot.PivotPositions.Source.get() )

    def atPositionToss(self) -> bool: 
        return self.atPosition( Pivot.PivotPositions.Toss.get() )

    def atPositionEject(self) -> bool: 
        return self.atPosition( Pivot.PivotPositions.Eject.get() )

    def syncEncoder(self):
        self.pivot.syncEncoder()