from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import PowerDistribution

class PDP(Subsystem):
    """
    PDP Subsystem
    """

    def __init__(self):
        """
        Initialization
        """
        self.pdp: PowerDistribution = PowerDistribution()
        self.pdp.resetTotalEnergy()

    def periodic(self):
        """
        Periodic Loop
        """    
        channelCount = 16 if self.pdp.getType() == PowerDistribution.ModuleType.kCTRE else 24

        tbl = NetworkTableInstance.getDefault().getTable("PowerDistribution")
        tbl.putNumber( "ChannelCount", channelCount )
        tbl.putNumber( "Temperature" , self.pdp.getTemperature() )
        tbl.putNumber( "TotalCurrent", self.pdp.getTotalCurrent() )
        tbl.putNumber( "TotalEnergy" , self.pdp.getTotalEnergy() )
        tbl.putNumber( "TotalPower"  , self.pdp.getTotalPower() )
        tbl.putNumber( "Voltage"     , self.pdp.getVoltage() )

        tbl.putNumber( "Faults/Brownouts" , self.pdp.getFaults().Brownout )
        tbl.putNumber( "Faults/CanWarning" , self.pdp.getFaults().CanWarning )

        tbl.putNumber( "StickFaults/Brownouts" , self.pdp.getStickyFaults().Brownout )
        tbl.putNumber( "StickFaults/CanBusOff" , self.pdp.getStickyFaults().CanBusOff )
        tbl.putNumber( "StickFaults/CanWarning" , self.pdp.getStickyFaults().CanWarning )

        for i in range( channelCount ):
            tbl.putNumber( f"ChannelCurrent/{i}", self.pdp.getCurrent(i) )
            tbl.putBoolean( f"Faults/Breakers/{i}", self.pdp.getFaults().getBreakerFault(i) )
            tbl.putBoolean( f"StickFaults/Breakers/{i}", self.pdp.getStickyFaults().getBreakerFault(i) )
