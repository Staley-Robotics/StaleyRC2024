"""
Description: Pigeon2 Extended Class
Version:  1
Date:  2024-01-09
"""
# Built-In Imports
import typing

# FRC Imports
# from phoenix5 import ErrorCode
# from phoenix5.sensors import WPI_Pigeon2, PigeonIMU_StatusFrame
from phoenix6.hardware import Pigeon2
from ntcore import NetworkTableInstance
from wpilib import RobotBase
from wpimath import units

# Our Imports
from .GyroIO import GyroIO
from util import *

class GyroIOPigeon2(Pigeon2, GyroIO):
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
        super().__init__( deviceNumber, "canivore1" )

        # Configure Default / Start Settings
        # self.configFactoryDefault()
        # self.zeroGyroBiasNow()
        self.setYaw( startYaw )
        #self.setStatusFramePeriod(PigeonIMU_StatusFrame.PigeonIMU_BiasedStatus_2_Gyro, 20)

        # Update the Sim Collection (if running in Simulator)
        if RobotBase.isSimulation():
            self.sim_state.set_raw_yaw( startYaw ) #getSimCollection().setRawHeading( startYaw )

    def updateInputs(self, inputs:GyroIO.GyroIOInputs):
        """
        Update GyroInputs Values for Logging Purposes
        :param inputs: GyroInputs objects that need to be updated
        """
        # yprDegrees = self.getYawPitchRoll()[1]
        # xyzDps = self.getRawGyro()[1]

        # inputs.connected = self.getLastError() == ErrorCode.OK
        inputs.rollPositionRad = units.degreesToRadians( self.get_roll().value ) # yprDegrees[1] )
        inputs.pitchPositionRad = units.degreesToRadians( -self.get_pitch().value ) # -yprDegrees[2] )
        inputs.yawPositionRad = units.degreesToRadians( self.get_yaw().value ) # yprDegrees[0] )
        inputs.rollVelocityRadPerSec = units.degreesToRadians( self.get_angular_velocity_y_device().value ) # xyzDps[1] )
        inputs.pitchVelocityRadPerSec = units.degreesToRadians( -self.get_angular_velocity_x_device().value ) # -xyzDps[0] )
        inputs.yawVelocityRadPerSec = units.degreesToRadians( self.get_angular_velocity_z_device().value ) # xyzDps[2] )

    def simulationPeriodic(self, velocity:float) -> None:
        """
        Run a periodic loop during Simulations
        :param velocity: The current Velocity in Radians Per Second
        """
        velocDegPerSec = units.radiansToDegrees( velocity )
        velocDegPer20ms = velocDegPerSec * 0.02 # Rio Loop Cycle
        self.sim_state.add_yaw( velocDegPer20ms ) #getSimCollection().addHeading( velocDegPer20ms )
        #newYaw = self.getYaw()
        while self.get_yaw() < 0:
            self.sim_state.set_raw_yaw( self.get_yaw().value + 360 ) #getSimCollection().setRawHeading( self.getYaw() + 360 )
        while self.get_yaw() >= 360.0: 
            self.sim_state.set_raw_yaw( self.get_ywaw().value - 360 ) #getSimCollection().setRawHeading( self.getYaw() - 360 )

