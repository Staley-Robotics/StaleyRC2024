"""
Description: Mechanism2D Container Class (currently in testing phase)
Version:  1
Date: 2023
"""

# FRC Imports
import wpilib
import wpimath.geometry
import commands2.button

# Self made classes
from util import *
import math

class Mechanism2D:
    def __init__(self) -> None:
        super().__init__()


        # Declare Mechanism settings
        self.kElevatorMinimumLength = NTTunableFloat("Mechanism2D/elevatorMinimunLength", 2.0, None, True)
        
        # self.elevatorEncoder = wpilib.Encoder(1, 2, True, wpilib.Encoder.EncodingType.k1X)

        # Tunables-unables
        self.angleIncrement = NTTunableFloat("Mechanism2D/angleIncrement", 5, None, True)

        self.angleIncrementIncrement = NTTunableFloat("Mechanism2D/angleIncrementIncrement", 1, None, True) #heheheheehehehheh incrementIncRemEnt

        # self.newAngle = 
        self.wristAngleStart = NTTunableFloat("Mechanism2D/wristAngle", 0, None, True)

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
            "wrist", 0.5, self.wristAngleStart.get(), color=wpilib.Color8Bit(wpilib.Color.kPurple)
        )
        self.wrist1 = self.wrist.appendLigament(
            "wirst1", 0.25, 90, color=wpilib.Color8Bit(wpilib.Color.kChocolate)
        )

        # post the mechanism to the dashboard (do this in robotcontainer)
        wpilib.SmartDashboard.putData("Mech2d", self.mech)
        wpilib.SmartDashboard.putNumber("Wrist Angle1", self.wristAngleStart.get())

        # post some variables (like angle increment)
        wpilib.SmartDashboard.putNumber("AngleIncrement", self.angleIncrement.get())


    def periodic(self):
        # update the dashboard mechanism's state
        self.elevator.setLength(
            self.kElevatorMinimumLength.get()
        )
        # self.wrist.setAngle(
        #     # self.wristAngle.get()
        # )
        print("If you see this a lot, periodic works... if not, then no")

        
        

    # def increaseElevatorHeight(self):
    #     """Increases the minimun height of the elevator"""
    #     self.kElevatorMinimumLength.set(self.kElevatorMinimumLength.get() + 1)

    def wristToAngle(self):
        """Sets heading of wrist to the direction of the left stick"""


    def get(self):
        """
        Gets the actual Mechanism
        """
        return self.mech