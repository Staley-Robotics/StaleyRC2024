"""
Description: Pigeon2 Extended Class on Phoenix6 Firmware
Version:  1
Date:  2024-01-09
"""

# Python Built-In Imports
import typing

# FRC imports
from phoenix6 import StatusCode
from phoenix6.hardware import Pigeon2
from phoenix6.configs import Pigeon2Configuration
from ntcore import NetworkTableInstance
from wpilib import RobotBase
from wpimath import units
from wpimath.geometry import Rotation2d

# Team Imports
from .Gyro import Gyro

class GyroPigeon2Phx6(Pigeon2, Gyro):
    """
    Custom Pigeon Class extends Pigeon2 with logging capabilities
    """

    def __init__( self, deviceNumber:int, canbus:str = '', startYaw:float = 0.0 ):
        """
        Constructure for a custom WPI_Piegon2 with logging

        :param deviceNumber: CAN Device ID of the Pigeon 2.
        :param canbus: Name of the CANbus; can be a CANivore device name or serial number.
                     Pass in nothing or "rio" to use the roboRIO.
        :param startYaw: Starting Yaw in Degrees once the Pigeon 2 is initialized.
        """
        # Initialize Pigeon2
        super().__init__( deviceNumber, canbus )

        # Configure Default / Start Settings
        #self.configFactoryDefault()
        #self.zeroGyroBiasNow()
        #self.setYaw(startYaw)
        #self.setStatusFramePeriod(PigeonIMU_StatusFrame.PigeonIMU_BiasedStatus_2_Gyro, 20)

        # Reset Configuration
        cfg = Pigeon2Configuration()
        self.configurator.apply( Pigeon2Configuration() )
        
        # Reset Status Frame Period
        self.get_yaw().set_update_frequency( 100 )
        self.get_pitch().set_update_frequency( 100 )
        self.get_roll().set_update_frequency( 100 )

        self.get_gravity_vector_x().set_update_frequency( 100 )
        self.get_gravity_vector_y().set_update_frequency( 100 )
        self.get_gravity_vector_z().set_update_frequency( 100 )

        # Reset the Yaw
        self.set_yaw( startYaw )

    def updateInputs(self, inputs:Gyro.GyroInputs):
        """
        Update GyroInputs Values for Logging Purposes
        :param inputs: GyroInputs objects that need to be updated
        """
        yprDegrees = self.getYawPitchRoll()[1]
        xyzDps = self.getRawGyro()[1]

        inputs.connected = xyzDps[0] == StatusCode.OK
        inputs.rollPositionRad = units.degreesToRadians( yprDegrees[1] )
        inputs.pitchPositionRad = units.degreesToRadians( -yprDegrees[2] )
        inputs.yawPositionRad = units.degreesToRadians( yprDegrees[0] )
        inputs.rollVelocityRadPerSec = units.degreesToRadians( xyzDps[1] )
        inputs.pitchVelocityRadPerSec = units.degreesToRadians( -xyzDps[0] )
        inputs.yawVelocityRadPerSec = units.degreesToRadians( xyzDps[2] )
    
    # def simulationPeriodic(self, velocity:typing.Callable[[],None]) -> None:
    #     """
    #     Run a periodic loop during Simulations
    #     :param velocity: A callable method to get the current Velocity in Radians Per Second
    #     """
    #     pass

    def getYaw(self) -> float:
        """
        Get Yaw

        :returns float in rotations?
        """
        return self.get_yaw().value_as_double

    def getPitch(self) -> float:
        """
        Get Pitch

        :returns float in rotations?
        """
        return self.get_pitch().value_as_double
    
    def getRoll(self) -> float:
        """
        Get Roll

        :returns float in rotations?
        """
        return self.get_roll().value_as_double
    
    def getYawPitchRoll(self):
        """
        Get the Yaw, Pitch, and Roll

        :returns [GyroError, [y,p,r]] in rotations?
        """
        ypr = [
            self.getYaw(),
            self.getPitch(),
            self.getRoll()
        ]
        err = self.get_yaw().status
        return [ err, ypr ]
    
    def getRawGyro(self):
        """
        Get angular velocity of the X, Y, and Z axises

        :returns [GyroError, [x,y,z]] in rotations per second
        """
        xyz = [
            self.get_angular_velocity_x_device().value_as_double,
            self.get_angular_velocity_y_device().value_as_double,
            self.get_angular_velocity_z_device().value_as_double
        ]
        err = self.get_angular_velocity_x_device().status
        return [ err, xyz ]
    
    def getRotation2d(self) -> Rotation2d:
        """
        Returns the heading of the robot as a frc#Rotation2d.
        The angle increases as the Pigeon 2 turns counterclockwise when looked at from the top. This follows the NWU axis convention.
        
        The angle is continuous; that is, it will continue from 360 to 361 degrees. This allows for algorithms that wouldn't want to see a discontinuity in the gyro output as it sweeps past from 360 to 0 on the second time around.

        :returns: The current heading of the robot as a frc#Rotation2d
        """
        return Rotation2d().fromDegrees( self.getYaw() )