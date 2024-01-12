"""
Description: Gyro Container Class
Version:  1
Date:  2024-01-09
"""

# Built-In Python Imports
import dataclasses

# FRC Imports
from ntcore import *
from wpimath.geometry import Rotation2d
import wpiutil.wpistruct

class Gyro:
    """
    Custom Pigeon Abstract Class used to extend a Gyro with our logging capabilities
    """

    @wpiutil.wpistruct.make_wpistruct(name="GyroInputs")
    @dataclasses.dataclass
    class GyroInputs:
        """
        A WPIStruct Object that contains all Gyro Reading Data.
        This is intended to simplify logging of this data.
        """
        connected: bool = False
        rollPositionRad: float = 0.0
        pitchPositionRad: float = 0.0
        yawPositionRad: float = 0.0
        rollVelocityRadPerSec: float = 0.0
        pitchVelocityRadPerSec: float = 0.0
        yawVelocityRadPerSec: float = 0.0

    def updateInputs(self, inputs:GyroInputs):
        """
        Update GyroInputs Values for Logging Purposes
        :param inputs: GyroInputs objects that need to be updated
        """
        inputs.connected = False
        inputs.rollPositionRad = 0.0
        inputs.pitchPositionRad = 0.0
        inputs.yawPositionRad = 0.0
        inputs.rollVelocityRadPerSec = 0.0
        inputs.pitchVelocityRadPerSec = 0.0
        inputs.yawVelocityRadPerSec = 0.0

    def getRotation2d(self) -> Rotation2d:
        """Returns the heading of the robot as a frc#Rotation2d.
        The angle increases as the Pigeon 2 turns counterclockwise when looked at from the top. This follows the NWU axis convention.
        
        The angle is continuous; that is, it will continue from 360 to 361 degrees. This allows for algorithms that wouldn't want to see a discontinuity in the gyro output as it sweeps past from 360 to 0 on the second time around.

        :returns: The current heading of the robot as a frc#Rotation2d
        """
        return Rotation2d()