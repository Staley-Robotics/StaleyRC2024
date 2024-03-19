"""
Description: Pigeon2 Extended Class
Version:  1
Date:  2024-01-09
"""
# Built-In Imports
import typing

# FRC Imports
from phoenix5 import ErrorCode
from phoenix5.sensors import WPI_Pigeon2, PigeonIMU_StatusFrame
from ntcore import NetworkTableInstance
from wpilib import RobotBase
from wpimath import units

# Our Imports
from .GyroIO import GyroIO
from util import *

class GyroIOPigeon2(WPI_Pigeon2, GyroIO):
    """
    Custom Pigeon Class extends WPI_Pigeon2 with logging capabilities
    """

    def __init__( self, deviceNumber:int, startYaw:float = 0.0 ):
        """
        Constructure for a custom WPI_Piegon2 with logging

        :param deviceNumber: CAN Device ID of the Pigeon 2.
        :param canbus: Name of the CANbus; can be a CANivore device name or serial number.
                     Pass in nothing or "rio" to use the roboRIO.
        :param startYaw: Starting Yaw in Degrees once the Pigeon 2 is initialized.
        """
        # Initialize WPI_Pigeon2
        gyroCanBus = NTTunableString( "/Config/SwerveDrive/Gyro/CanBus", "canivore1", persistent=False )
        super().__init__( deviceNumber, gyroCanBus.get() )

        # Configure Default / Start Settings
        self.configFactoryDefault()
        self.zeroGyroBiasNow()
        self.setYaw( startYaw )
        self.setStatusFramePeriod(PigeonIMU_StatusFrame.PigeonIMU_BiasedStatus_2_Gyro, 20)

        # Update the Sim Collection (if running in Simulator)
        if RobotBase.isSimulation():
            self.getSimCollection().setRawHeading( startYaw )

    def updateInputs(self, inputs:GyroIO.GyroIOInputs):
        """
        Update GyroInputs Values for Logging Purposes
        :param inputs: GyroInputs objects that need to be updated
        """
        yprDegrees = self.getYawPitchRoll()[1]
        xyzDps = self.getRawGyro()[1]

        inputs.connected = self.getLastError() == ErrorCode.OK
        inputs.rollPositionRad = units.degreesToRadians( yprDegrees[1] )
        inputs.pitchPositionRad = units.degreesToRadians( -yprDegrees[2] )
        inputs.yawPositionRad = units.degreesToRadians( yprDegrees[0] )
        inputs.rollVelocityRadPerSec = units.degreesToRadians( xyzDps[1] )
        inputs.pitchVelocityRadPerSec = units.degreesToRadians( -xyzDps[0] )
        inputs.yawVelocityRadPerSec = units.degreesToRadians( xyzDps[2] )

    def simulationPeriodic(self, velocity:float) -> None:
        """
        Run a periodic loop during Simulations
        :param velocity: The current Velocity in Radians Per Second
        """
        velocDegPerSec = units.radiansToDegrees( velocity )
        velocDegPer20ms = velocDegPerSec * 0.02 # Rio Loop Cycle
        self.getSimCollection().addHeading( velocDegPer20ms )
        #newYaw = self.getYaw()
        while self.getYaw() < 0:
            self.getSimCollection().setRawHeading( self.getYaw() + 360 )
        while self.getYaw() >= 360.0: 
            self.getSimCollection().setRawHeading( self.getYaw() - 360 )

