from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import RobotState

from util import *
from .PivotIO import PivotIO

class Pivot(Subsystem):
    class PivotPositions:
        Upward = NTTunableFloat( "/Config/PivotPositions/Upward", 55.041, persistent=True )
        Handoff = NTTunableFloat( "/Config/PivotPositions/Handoff", 32.168, persistent=True )
        Amp = NTTunableFloat( "/Config/PivotPositions/Amp", -45.0, persistent=True )
        Trap = NTTunableFloat( "/Config/PivotPositions/Trap", -60.0, persistent=True )
        Source = NTTunableFloat( "/Config/PivotPositions/Source", -60.0, persistent=True )
        Downward = NTTunableFloat( "/Config/PivotPositions/Downward", -52.031, persistent=True )

    def __init__(self, pivot:PivotIO):
        self.pivot = pivot
        self.pivotInputs = pivot.PivotIOInputs
        self.pivotLogger = NetworkTableInstance.getDefault().getStructTopic( "/Pivot", PivotIO.PivotIOInputs ).publish()
        
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
        #??? Don't Need It (Desired State / Current State)
            
    def set(self, position:float):
        self.pivot.setPosition( position )

    def stop(self):
        self.set( self.pivot.getPosition() )

    # def handoff(self):
    #     self.set( self.PivotPositions.Handoff )

    # def amp(self):
    #     self.set( self.PivotPositions.Amp )
    
    # def trap(self):
    #     self.set( self.PivotPositions.Trap )

    def atSetpoint(self) -> bool:
        self.pivot.atSetpoint( 1.0 )