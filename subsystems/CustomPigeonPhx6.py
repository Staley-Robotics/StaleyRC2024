import typing

from phoenix6 import StatusCode
from phoenix6.hardware import Pigeon2
from phoenix6.configs import Pigeon2Configuration
from ntcore import NetworkTableInstance
from wpilib import RobotBase
from wpimath import units
from wpimath.geometry import Rotation2d

class CustomPigeonPhx6(Pigeon2):
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

        self.set_yaw( startYaw )
        
        # Update the Sim Collection (if running in Simulator)
        #if RobotBase.isSimulation():
        #    self.getSimCollection().setRawHeading( startYaw )

    def updateSysOutputs(self):
        """
        Update Network Table Logging
        """
        yprDegrees = self.getYawPitchRoll()[1]
        xyzDps = self.getRawGyro()[1]
        

        tbl = NetworkTableInstance.getDefault().getTable( "SysOutputs/SwerveDrive/Gyro" )
        tbl.putBoolean( "connected", xyzDps[0] == StatusCode.OK )
        tbl.putNumber( "rollPositionRad", units.degreesToRadians( yprDegrees[1] ) )
        tbl.putNumber( "pitchPositionRad", units.degreesToRadians( -yprDegrees[2] ) )
        tbl.putNumber( "yawPositionRad", units.degreesToRadians( yprDegrees[0] ) )
        tbl.putNumber( "rollVelocityRadPerSec", units.degreesToRadians( xyzDps[1] ) )
        tbl.putNumber( "pitchVelocityRadPerSec", units.degreesToRadians( -xyzDps[0] ) )
        tbl.putNumber( "yawVelocityRadPerSec", units.degreesToRadians( xyzDps[2] ) )

    def getYaw(self) -> float:
        return self.get_yaw().value_as_double

    def getPitch(self) -> float:
        return self.get_pitch().value_as_double
    
    def getRoll(self) -> float:
        return self.get_roll().value_as_double
    
    def getYawPitchRoll(self):
        ypr = [
            self.getYaw(),
            self.getPitch(),
            self.getRoll()
        ]
        err = self.get_yaw().status
        return [ err, ypr ]
    
    def getRawGyro(self):
        xyz = [
            self.get_angular_velocity_x_device().value_as_double,
            self.get_angular_velocity_y_device().value_as_double,
            self.get_angular_velocity_z_device().value_as_double
        ]
        err = self.get_angular_velocity_x_device().status
        return [ err, xyz ]
    
    def getRotation2d(self):
        return Rotation2d().fromDegrees( self.getYaw() )