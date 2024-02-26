"""
Description: Mechanism2DToStick Container Class (Finished... I think)
Version:  1
Date: 2024
"""

# FRC Imports
import wpilib
import wpimath.geometry
import commands2.button

# Self made classes
from util import *
import math

class Mechanism2DToStick:
    def __init__(self) -> None:
        super().__init__()

        # Name controller
        self.m_driver1 = commands2.button.CommandXboxController(0)

        # Declare Mechanism settings
        self.kElevatorMinimumLength = NTTunableFloat("Mechanism2DStick/elevatorMinimunLength", 2.0, None, True)
        
        # self.elevatorEncoder = wpilib.Encoder(1, 2, True, wpilib.Encoder.EncodingType.k1X)

        # Tunables-unables
        self.wristVector = NTTunableFloat("Mechanism2DToStick/wristVector", 0, None, True)

        # self.newAngle = 
        self.wristAngleStart = NTTunableFloat("Mechanism2DToStick/wristAngleStart", 0, None, True)

        # the main mechanism object
        self.mech = wpilib.Mechanism2d(3, 3)
        
        # a mechanism root node
        self.root = self.mech.getRoot("arm", 2, 0)

        # Vector stuff for later
        self.PI = math.pi
        self.theta = 0

        # MechanismLigament2d objects represent each "section"/"stage" of the mechanism, and are based
        # off the root node or another ligament object
        self.elevator = self.root.appendLigament(
            "elevator", self.kElevatorMinimumLength.get(), 90, color=wpilib.Color8Bit(wpilib.Color.kOrange)
        )
        self.wrist = self.elevator.appendLigament(
            "wrist", 0.5, self.wristAngleStart.get(), color=wpilib.Color8Bit(wpilib.Color.kPurple)
        )
        self.hand = self.wrist.appendLigament(
            "hand", 0.25, 90, color=wpilib.Color8Bit(wpilib.Color.kChocolate)
        )

        # post the mechanism to the dashboard (do this in robotcontainer)
        # wpilib.SmartDashboard.putData("Mech2DToStick", self.mech)
        wpilib.SmartDashboard.putNumber("Wrist Angle Start", self.wristAngleStart.get())

        # post some variables (like wristVector)


    def periodic(self):
        # update the dashboard mechanism's state
        self.elevator.setLength(
            self.kElevatorMinimumLength.get()
        )
        # self.wrist.setAngle(
        #     # self.wristAngle.get()
        # )
        print("If you see this a lot, periodic works... if not, then no")

        
    def wristToAngle(self):
        """Sets heading of wrist to the direction of the left stick"""
        # print(f"INPUT X: {_inputX} \n")
        _inputX = self.m_driver1.getLeftX()
        _inputY = self.m_driver1.getLeftY()
        # print(f"inputX: {_inputX}") #telemetry
        # print(f"inputY: {_inputY}") #telemetry
        # self.wristVector.set(360 * (_inputX + _inputY)) # multiplying by 360 because the inputs are going to be inbetween -1 and 1... subject to change
        # self.wrist.setAngle(self.wristVector.get())
        # self.wrist.setAngle(180*(_inputX + _inputY)) 


        direction = math.degrees(math.atan(_inputX/_inputY))
        if _inputY > 0: # this code allows the mech's wrist to rotate past 180 degrees.
            direction += 180

        print("direction:", direction) #telemetry
        if round(_inputX, 1) != 0 or round(_inputY, 1) != 0:
            self.wrist.setAngle(direction)    
        
        # print("IT WORKED")
        #Testing bullshdihtlsd
        #btw I completely forgot what the code below does but oh well ¯\_(ツ)_/¯
        # robotInputY = ((_inputX * math.sin(self.theta)) + (_inputY * math.sin(self.theta + (self.PI / 2)))); # *1.4
        # robotInputX = (_inputX * math.cos(self.theta)) + (_inputY * math.cos(self.theta + (self.PI / 2)))
        # print(f"robotInputX: {robotInputX}")
        # print(f"robotInputY: {robotInputY}")
        # self.wrist.setAngle(180*(robotInputX + robotInputY))

    # def handToAngle(self):
    #     """Sets the heading of hand to the direction of the right stick"""
    #     _inputX = self.m_driver1.getRightX()
    #     _inputY = self.m_driver1.getRightY()

    #     direction = math.degrees(math.atan(_inputX/_inputY))
    #     if _inputY > 0: # this code allows the mech's hand to rotate past 180 degrees
    #         direction += 180

    #     if round(_inputX, 1) != 0 or round(_inputY, 1) != 0: # only moves the hand if the joystick has moved enough
    #         self.wrist.setAngle(direction)

    # def rotateHand(self): #old version
    #     """
    #     Rotates the hand controlled by triggers.
        
    #     Right trigger will turn the hand clockwise.
    #     Left trigger will turn the hand counterclockwise.
    #     """
    #     right_trigger_input = self.m_driver1.getRightTriggerAxis()
    #     left_trigger_input = self.m_driver1.getLeftTriggerAxis()

    #     speed = 5 * (left_trigger_input - right_trigger_input)

    #     self.hand.setAngle(self.hand.getAngle() + speed)

    def handToAngle(self):
        """Sets heading of hand to the direction of the right stick"""
        # print(f"INPUT X: {_inputX} \n")
        _inputX = self.m_driver1.getLeftTriggerAxis()
        _inputY = self.m_driver1.getRightTriggerAxis()


        robotInputY = (_inputX * math.sin(self.theta)) + (_inputY * math.sin(self.theta + (self.PI / 2)))
        robotInputX = (_inputX * math.cos(self.theta)) + (_inputY * math.cos(self.theta + (self.PI / 2)))


        
        direction = math.degrees(math.atan(_inputX/_inputY)) - self.wrist.getAngle()

        if _inputY > 0: # this code allows the mech's wrist to rotate past 180 degrees.
            direction += 180

        print("H_direction:", direction) #telemetry
        if round(_inputX, 1) != 0 or round(_inputY, 1) != 0:
            self.hand.setAngle(direction)

    def update(self):
        self.wristToAngle()
        self.handToAngle()

    def get(self):
        """
        Gets the actual Mechanism
        """
        return self.mech