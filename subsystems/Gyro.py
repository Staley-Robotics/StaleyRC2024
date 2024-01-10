"""
Description: Gyro Container Class
Version:  1
Date:  2024-01-09
"""

# FRC Imports
from wpimath.geometry import Rotation2d

class Gyro:
    """
    Custom Pigeon Abstract Class used to extend a Gyro with our logging capabilities
    """

    def updateOutputs(self):
        """
        Update Network Table Logging
        """
        raise NotImplementedError( "SwerveModule.updateOutputs() must created in child class." )

    def getRotation2d(self) -> Rotation2d:
        """Returns the heading of the robot as a frc#Rotation2d.
        The angle increases as the Pigeon 2 turns counterclockwise when looked at from the top. This follows the NWU axis convention.
        
        The angle is continuous; that is, it will continue from 360 to 361 degrees. This allows for algorithms that wouldn't want to see a discontinuity in the gyro output as it sweeps past from 360 to 0 on the second time around.

        :returns: The current heading of the robot as a frc#Rotation2d
        """
        return Rotation2d()