from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import RobotState

from util import *
from .PivotIO import PivotIO

class Pivot(Subsystem):
    class PivotPositions:
        __priv__ = {
            0: NTTunableFloat( "/Config/PivotPositions/Upward", 70.0 ),
            1: NTTunableFloat( "/Config/PivotPositions/Handoff", 30.0 ),
            2: NTTunableFloat( "/Config/PivotPositions/Amp", -45.0 ),
            3: NTTunableFloat( "/Config/PivotPositiosn/Trap", -60.0 ),
            4: NTTunableFloat( "/Config/PivotPositions/Downward", -70.0 ),
        }
        Upward = __priv__[0].get()
        Handoff = __priv__[0].get()
        Amp = __priv__[0].get()
        Trap = __priv__[0].get()
        Downward = __priv__[0].get()

    def __init__(self, pivot:PivotIO):
        self.pivot = pivot
        self.pivotInputs = pivot.PivotIOInputs
        self.pivotLogger = NetworkTableInstance.getDefault().getStructTopic( "/Pivot", PivotIO.PivotIOInputs ).publish()
        
        self.offline = NTTunableBoolean( "/OfflineOverride/Pivot", False )

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