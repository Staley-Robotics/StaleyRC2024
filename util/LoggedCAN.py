import dataclasses
import typing

from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import PowerDistribution

from wpilib import CANData, CANStatus
import wpiutil.wpistruct

class LoggedCAN:
    """
    CAN Subsystem
    """
    @wpiutil.wpistruct.make_wpistruct( name="LoggedCANInputs" )
    @dataclasses.dataclass
    class LoggedCANInputs:
        percentBusUtilization:float = 0.0
        busOffCount:int = 0
        receiveErrorCount:int = 0
        transmitErrorCount:int = 0
        txFullCount:int = 0

    def __init__(self):
        self.canStatus = CANStatus()
        self.canInputs = LoggedCAN.LoggedCANInputs()
        self.canLogger = NetworkTableInstance.getDefault().getStructTopic( "/SystemStats/CANData", LoggedCAN.LoggedCANInputs ).publish()

    def updateInputs(self, inputs:LoggedCANInputs):
        inputs.percentBusUtilization = self.canStatus.percentBusUtilization
        inputs.busOffCount = self.canStatus.busOffCount
        inputs.receiveErrorCount = self.canStatus.receiveErrorCount
        inputs.transmitErrorCount = self.canStatus.transmitErrorCount
        inputs.txFullCount = self.canStatus.txFullCount

    def periodic(self):
        self.updateInputs( self.canInputs )
        self.canLogger.set( self.canInputs )