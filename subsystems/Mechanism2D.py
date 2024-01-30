"""
Description: Mechanism2D Container Class (currently in testing phase)
Version:  1
Date: 2023
"""

# FRC Imports
import wpilib

# Self made classes
from util import *


class Mechanism2D():
    def __init__(self) -> None:
        super().__init__()

        # Declare Mechanism settings
        self.kElevatorMinimumLength = NTTunableFloat("Mechanism2D/elevatorMinimunLength", 2.0, None, True)
        
        self.elevatorEncoder = wpilib.Encoder(1, 2, True, wpilib.Encoder.EncodingType.k1X)

        # the main mechanism object
        self.mech = wpilib.Mechanism2d(3, 3)
        # a mechanism root node
        self.root = self.mech.getRoot("arm", 2, 0)

        # MechanismLigament2d objects represent each "section"/"stage" of the mechanism, and are based
        # off the root node or another ligament object
        self.elevator = self.root.appendLigament(
            "elevator", self.kElevatorMinimumLength.get(), 90, color=wpilib.Color8Bit(wpilib.Color.kOrange)
        )
        self.wrist = self.elevator.appendLigament(
            "wrist", 0.5, 90, 6, wpilib.Color8Bit(wpilib.Color.kPurple)
        )

        # post the mechanism to the dashboard
        wpilib.SmartDashboard.putData("Mech2d", self.mech)


    def robotPeriodic(self):
        # update the dashboard mechanism's state
        self.elevator.setLength(
            self.kElevatorMinimumLength + self.elevatorEncoder.getDistance()
        )
        self.wrist.setAngle(self.wrist.getAngle())