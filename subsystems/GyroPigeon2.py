"""
Description: Pigeon2 Extended Class
Version:  1
Date:  2024-01-09
"""

# FRC Imports
from phoenix5 import ErrorCode
from phoenix5.sensors import WPI_Pigeon2, PigeonIMU_StatusFrame
from ntcore import NetworkTableInstance
from wpilib import RobotBase
from wpimath import units

# Our Imports
from .Gyro import Gyro

class GyroPigeon2(WPI_Pigeon2, Gyro):
    """
    Custom Pigeon Class extends WPI_Pigeon2 with logging capabilities
    """

    def __init__( self, deviceNumber:int, canbus:str = '', startYaw:float = 0.0 ):
        """
        Constructure for a custom WPI_Piegon2 with logging

        :param deviceNumber: CAN Device ID of the Pigeon 2.
        :param canbus: Name of the CANbus; can be a CANivore device name or serial number.
                     Pass in nothing or "rio" to use the roboRIO.
        :param startYaw: Starting Yaw in Degrees once the Pigeon 2 is initialized.
        """
        # Initialize WPI_Pigeon2
        super().__init__( deviceNumber, canbus )

        # Configure Default / Start Settings
        self.configFactoryDefault()
        self.zeroGyroBiasNow()
        self.setYaw(startYaw)
        self.setStatusFramePeriod(PigeonIMU_StatusFrame.PigeonIMU_BiasedStatus_2_Gyro, 20)

        # Update the Sim Collection (if running in Simulator)
        if RobotBase.isSimulation():
            self.getSimCollection().setRawHeading( startYaw )

    def updateInputs(self, inputs:Gyro.GyroInputs):
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
