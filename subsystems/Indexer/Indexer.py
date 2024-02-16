from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import DriverStation

from util import *
from .IndexerIO import IndexerIO

class Indexer(Subsystem):
    class IndexerSpeeds:
        __priv__ = {
            0: NTTunableFloat( "/Config/IndexerSpeeds/Handoff", 0.35 ),
            1: NTTunableFloat( "/Config/IndexerSpeeds/Launch", 0.50 ),
            2: NTTunableFloat( "/Config/IndexerSpeeds/Eject", -1.0 ),
            3: NTTunableFloat( "/Config/IndexerSpeeds/SelfIn", 0.05 ),
            4: NTTunableFloat( "/Config/IndexerSpeeds/SelfOut", -0.05 )
        }
        Stop = 0
        Handoff = __priv__[0].get()
        Launch = __priv__[1].get()
        Eject = __priv__[2].get()
        SelfIn = __priv__[3].get()
        SelfOut = __priv__[4].get()

    def __init__(self, indexer:IndexerIO):
        self.indexer = indexer
        self.indexerInputs = indexer.IndexerIOInputs()
        self.indexerLogger = NetworkTableInstance.getDefault().getStructTopic( "/Indexer", IndexerIO.IndexerIOInputs ).publish()

        self.offline = NTTunableBoolean( "/OfflineOverride/Indexer", False )

    def periodic(self):
        # Logging
        self.indexer.updateInputs( self.indexerInputs )
        self.indexerLogger.set( self.indexerInputs )
        #NewLogger# Logger.getInstance().processInputs( "Indexer", self.indexerInputs )
        
        # Run Subsystem
        if DriverStation.isDisabled() or self.offline.get():
            self.stop()

        if False: #self.isCharacterizing.get():
            self.indexer.runCharacterization( self.charSettingsVolts.get(), self.charSettingsRotation.get() )
        else:
            ### Self Correct???
            self.indexer.run()

        # Post Run Logging
        #??? Don't Need It (Desired State / Current State)

    def set(self, speed:float):
        self.indexer.setVelocity( speed )

    def stop(self) -> None:
        self.set( self.IndexerSpeeds.Stop )

    # def handoff(self) -> None:
    #     self.set( self.IndexerSpeeds.Handoff )

    # def launch(self) -> None:
    #     self.set( self.IndexerSpeeds.Launch )

    # def eject(self) -> None:
    #     self.set( self.IndexerSpeeds.Eject )

    def setBrake(self, brake:bool) -> None:
        self.indexer.setBrake(brake)

    def hasNote(self) -> bool:
        return False
    
    def isRunning(self) -> bool:
        return ( self.indexer.getVelocity() != self.IndexerSpeeds.Stop )
