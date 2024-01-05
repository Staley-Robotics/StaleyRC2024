"""
Description: Swerve Module Container Class
Version:  1
Date:  2024-01-03
"""

### Imports
# FRC Component Imports
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
from wpimath.geometry import Translation2d

# Class: SwerveModule
class SwerveModule:
    #def __init__(self, subsystemName:str, driveId:int, angleId:int, sensorId:int, posX:float, posY:float, angleOffset:float):
    #    pass

    def setDesiredState(self, desiredState:SwerveModuleState):
        return None

    def getReferencePosition(self) -> Translation2d:
        return None
       
    def getModuleState(self) -> SwerveModuleState:
        return None

    def getModulePosition(self) -> SwerveModulePosition:
        return None

