import dataclasses
import typing

from commands2 import Subsystem
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

        StickFaultsBrownouts:float = 0.0
        StickFaultsCanBusOff:float = 0.0
        StickFaultsCanWarning:float = 0.0

        #ChannelCurrent:float[24] = dataclasses.field( default_factory = float )
        FaultsBreakers:float = dataclasses.field( default_factory = float )
        #StickFaultsBreakers:list = dataclasses.field( default_factory = float )

        def __init__(self, channels):
            self.ChannelCount = channels
            #self.ChannelCurrent = list()
            faultsBreakers = list(range(channels))
            #self.StickFaultsBreakers = list()

            for i in range(self.ChannelCount):
                #self.ChannelCurrent.append( 0.0 )
                faultsBreakers[i] = 0.0
                #self.StickFaultsBreakers.append( 0.0 )

            print( faultsBreakers )
            self.FaultsBreakers = faultsBreakers

    def __init__(self):
        """
        Initialization
        """
        self.pdp: PowerDistribution = None
        try:
            self.pdp = PowerDistribution( 0, PowerDistribution.ModuleType.kCTRE )
            self.pdp.getVersion()
        except:
            self.pdp = PowerDistribution( 1, PowerDistribution.ModuleType.kRev )
        
        if self.pdp == None:
            return
        
        self.pdp.resetTotalEnergy()
        self.pdpLogger = NetworkTableInstance.getDefault().getStructTopic( "/PowerDistribution", LoggedPDP.LoggedPDPInputs ).publish()
        self.pdpInputs = self.LoggedPDPInputs( 24 )

    def updateInputs(self, inputs:LoggedPDPInputs):            
        inputs.Model = self.pdp.getType()
        #inputs.ChannelCount = channelCount
        inputs.Temperature = self.pdp.getTemperature()
        inputs.TotalCurrent = self.pdp.getTotalCurrent()
        inputs.TotalEnergy = self.pdp.getTotalEnergy()
        inputs.TotalPower = self.pdp.getTotalPower()
        inputs.Voltage = self.pdp.getVoltage()

        inputs.FaultsBrownouts = self.pdp.getFaults().Brownout
        inputs.FaultsCanWarning = self.pdp.getFaults().CanWarning

        inputs.StickFaultsBrownouts = self.pdp.getStickyFaults().Brownout
        inputs.StickFaultsCanBusOff = self.pdp.getStickyFaults().CanBusOff
        inputs.StickFaultsCanWarning = self.pdp.getStickyFaults().CanWarning

        for i in range( inputs.ChannelCount ):
            #inputs.ChannelCurrent[i] = self.pdp.getCurrent(i)
            inputs.FaultsBreakers[i] = self.pdp.getFaults().getBreakerFault(i)
            #inputs.StickFaultsBreakers[i] = self.pdp.getStickyFaults().getBreakerFault(i)

    def periodic(self):
        """
        Periodic Loop
        """
        if self.pdp == None:
            return
        
        self.updateInputs( self.pdpInputs )
        self.pdpLogger.set( self.pdpInputs )
