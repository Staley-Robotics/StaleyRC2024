import dataclasses
import typing

from ntcore import NetworkTableInstance
from wpilib import PowerDistribution

import wpiutil.wpistruct
import wpiutil

class LoggedPDP:
    """
    PDP Subsystem
    """
    @wpiutil.wpistruct.make_wpistruct( name="StructList" )
    @dataclasses.dataclass
    class StructList:
        zero:float = 0.0

    @wpiutil.wpistruct.make_wpistruct( name="LoggedPDPInputs" )
    @dataclasses.dataclass
    class LoggedPDPInputs:
        Model:float = 0.0
        ChannelCount:int = 24
        Temperature:float = 0.0
        TotalCurrent:float = 0.0
        TotalEnergy:float = 0.0
        TotalPower:float = 0.0
        Voltage:float = 0.0

        FaultsBrownouts:float = 0.0
        FaultsCanWarning:float = 0.0

        StickyFaultsBrownouts:float = 0.0
        StickyFaultsCanBusOff:float = 0.0
        StickyFaultsCanWarning:float = 0.0

        # ChannelCurrent:wpiutil.wpistruct.double = dataclasses.field( default_factory = tuple )
        # FaultsBreakers:bool = dataclasses.field( default_factory = bool )
        # StickyFaultsBreakers:bool = dataclasses.field( default_factory = bool )
        
        # def __post_init__(self):
        #     self.ChannelCurrent = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
        #     self.FaultsBreakers = [ False, False, False, False, False, False, False, False, False, False, False, False, 
        #                        False, False, False, False, False, False, False, False, False, False, False, False ]
        #     self.StickyFaultsBreakers = [ False, False, False, False, False, False, False, False, False, False, False, False, 
        #                              False, False, False, False, False, False, False, False, False, False, False, False ]
            
    def __init__(self, type:PowerDistribution.ModuleType = PowerDistribution.ModuleType.kCTRE, canId:int = None ):
        """
        Initialization
        """
        self.pdp: PowerDistribution = None
        channels = 0
        match type:
            case PowerDistribution.ModuleType.kCTRE:
                canId = 0 if canId == None else canId
                self.pdp = PowerDistribution( canId, PowerDistribution.ModuleType.kCTRE )
                channels = 16
            case PowerDistribution.ModuleType.kRev:
                canId = 1 if canId == None else canId
                self.pdp = PowerDistribution( canId, PowerDistribution.ModuleType.kRev )
                channels = 24
            case _:
                pass
        
        if self.pdp == None:
            return
        
        self.pdp.resetTotalEnergy()
        self.pdpLogger = NetworkTableInstance.getDefault().getStructTopic( "/PowerDistribution", LoggedPDP.LoggedPDPInputs ).publish()
        self.pdpLoggerChannelCurrent = NetworkTableInstance.getDefault().getFloatArrayTopic( "/PowerDistribution/ChannelCurrent" ).publish()
        self.pdpLoggerFaultsBreakers = NetworkTableInstance.getDefault().getBooleanArrayTopic( "/PowerDistribution/FaultBreakers" ).publish()
        self.pdpLoggerStickyFaultsBreakers = NetworkTableInstance.getDefault().getBooleanArrayTopic( "/PowerDistribution/StickyFaultsBreakers" ).publish()

        self.pdpInputs = self.LoggedPDPInputs()

        self.pdpInputs.ChannelCount = channels
        self.ChannelCurrent = [ 0 for x in range(channels) ]
        self.FaultsBreakers = [ False for x in range(channels) ]
        self.StickyFaultsBreakers = [ False for x in range(channels) ]

    def updateInputs(self, inputs:LoggedPDPInputs):            
        #inputs.Model = self.pdp.getType()
        
        inputs.Temperature = self.pdp.getTemperature()
        inputs.TotalCurrent = self.pdp.getTotalCurrent()
        inputs.TotalEnergy = self.pdp.getTotalEnergy()
        inputs.TotalPower = self.pdp.getTotalPower()
        inputs.Voltage = self.pdp.getVoltage()

        faults = self.pdp.getFaults()
        stickyFaults = self.pdp.getStickyFaults()

        inputs.FaultsBrownouts = faults.Brownout
        inputs.FaultsCanWarning = faults.CanWarning

        inputs.StickyFaultsBrownouts = stickyFaults.Brownout
        inputs.StickyFaultsCanBusOff = stickyFaults.CanBusOff
        inputs.StickyFaultsCanWarning = stickyFaults.CanWarning

        for i in range( inputs.ChannelCount ):
            self.ChannelCurrent[i] = self.pdp.getCurrent(i)
            self.FaultsBreakers[i] = faults.getBreakerFault(i)
            self.StickyFaultsBreakers[i] = stickyFaults.getBreakerFault(i)

    def periodic(self):
        """
        Periodic Loop
        """
        if self.pdp == None:
            return
        
        self.updateInputs( self.pdpInputs )
        self.pdpLogger.set( self.pdpInputs )
        self.pdpLoggerChannelCurrent.set( self.ChannelCurrent )
        self.pdpLoggerFaultsBreakers.set( self.FaultsBreakers )
        self.pdpLoggerStickyFaultsBreakers.set( self.StickyFaultsBreakers )
        