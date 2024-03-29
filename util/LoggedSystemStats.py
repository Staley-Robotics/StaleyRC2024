import dataclasses
import typing

import hal
from commands2 import Subsystem
from ntcore import NetworkTableInstance

from wpilib import CANStatus, RobotBase, getTime
import wpiutil.wpistruct

@wpiutil.wpistruct.make_wpistruct( name="LoggedSystemStatsInputs" )
@dataclasses.dataclass
class LoggedSystemStatsInputs:

    @wpiutil.wpistruct.make_wpistruct( name="LoggedCANInputs" )
    @dataclasses.dataclass
    class LoggedCANInputs:
        Utilization:float = 0.0
        OffCount:int = 0
        ReceiveErrorCount:int = 0
        TransmitErrorCount:int = 0
        TxFullCount:int = 0

    @wpiutil.wpistruct.make_wpistruct( name="LoggedRailInputs" )
    @dataclasses.dataclass
    class LoggedRailInputs:
        Active:bool = False
        Current:float = 0
        CurrentFaults:int = 0
        Voltage:float = 0


    Rail3v3:LoggedRailInputs = dataclasses.field( default_factory = LoggedRailInputs )
    Rail5v:LoggedRailInputs = dataclasses.field( default_factory = LoggedRailInputs )
    Rail6v:LoggedRailInputs = dataclasses.field( default_factory = LoggedRailInputs )
    CANBus:LoggedCANInputs = dataclasses.field( default_factory = LoggedCANInputs )

    BatteryCurrent:float = 0.0
    BatteryVoltage:float = 0.0
    BrownedOut:bool = False
    EpochTimeMicros:float = 0.0
    SystemActive:bool = False

    def __post_init__(self):
        self.CANBus = LoggedSystemStatsInputs.LoggedCANInputs()
        self.Rail3v3 = LoggedSystemStatsInputs.LoggedRailInputs()
        self.Rail5v = LoggedSystemStatsInputs.LoggedRailInputs()
        self.Rail6v = LoggedSystemStatsInputs.LoggedRailInputs()

class LoggedSystemStats:
    """
    System Stats Logger
    """
    def __init__(self):
        self.sysStatsInputs = LoggedSystemStatsInputs()
        self.sysStatsLogger = NetworkTableInstance.getDefault().getStructTopic( "/SystemStats", LoggedSystemStatsInputs ).publish()

    def updateInputs(self, inputs:LoggedSystemStatsInputs):
        # Raw Current / Voltage Data
        inputs.BatteryCurrent = hal.getVinCurrent()[0]
        inputs.BatteryVoltage = hal.getVinVoltage()[0]
        inputs.BrownedOut = hal.getBrownedOut()[0]
        # System Data
        inputs.EpochTimeMicros = getTime()
        inputs.SystemActive = hal.getSystemActive()[0]
        #3v3Rail
        inputs.Rail3v3.Active = hal.getUserActive3V3()[0]
        inputs.Rail3v3.Current = hal.getUserCurrent3V3()[0]
        inputs.Rail3v3.CurrentFaults = hal.getUserCurrentFaults3V3()[0]
        inputs.Rail3v3.Voltage = hal.getUserVoltage3V3()[0]
        #5vRail
        inputs.Rail5v.Active = hal.getUserActive5V()[0]
        inputs.Rail5v.Current = hal.getUserCurrent5V()[0]
        inputs.Rail5v.CurrentFaults = hal.getUserCurrentFaults5V()[0]
        inputs.Rail5v.Voltage = hal.getUserVoltage5V()[0]
        #6vRail
        inputs.Rail6v.Active = hal.getUserActive6V()[0]
        inputs.Rail6v.Current = hal.getUserCurrent6V()[0]
        inputs.Rail6v.CurrentFaults = hal.getUserCurrentFaults6V()[0]
        inputs.Rail6v.Voltage = hal.getUserVoltage6V()[0]
        #CANBus
        if RobotBase.isReal():
            canStatus = hal.CAN_GetCANStatus()
            if canStatus[5] == 0:
                inputs.CANBus.Utilization = canStatus[0]
                inputs.CANBus.OffCount = canStatus[1]
                inputs.CANBus.TxFullCount = canStatus[2]
                inputs.CANBus.ReceiveErrorCount = canStatus[3]
                inputs.CANBus.TransmitErrorCount = canStatus[4]
        
    def periodic(self):
        self.updateInputs( self.sysStatsInputs )
        self.sysStatsLogger.set( self.sysStatsInputs )

