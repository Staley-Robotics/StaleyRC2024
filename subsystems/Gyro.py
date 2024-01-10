"""
Description: Gyro Container Class
Version:  1
Date:  2024-01-09
"""

# FRC Imports
from wpimath.geometry import Rotation2d

class Gyro:
    def updateOutputs(self):
        pass

    def getRotation2d(self) -> Rotation2d:
        return Rotation2d()