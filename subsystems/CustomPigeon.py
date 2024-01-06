from ctre import ErrorCode
from ctre.sensors import WPI_Pigeon2, PigeonIMU_StatusFrame
from ntcore import NetworkTableInstance
from wpilib import RobotBase
from wpimath import units

class CustomPigeon(WPI_Pigeon2):
    """
    Custom Pigeon Class extends WPI_Pigeon2 with logging capabilities
    """

    def __init__( self, deviceNumber:int, canbus:str = '', startYaw:float = 0.0 ):
        """
        Constructure for a custom WPI_Piegon2 with logging

        :param deviceNumber: CAN Device ID of the Pigeon 2.
        :param canbus: Name of the CANbus; can be a CANivore device name or serial number.
                     Pass in nothing or "rio" to use the roboRIO.
        :param startYaw: Starting Yaw in Degrees once the Pigeon 2 is initialized.
        """
        # Initialize WPI_Pigeon2
        super().__init__( deviceNumber, canbus )

        # Configure Default / Start Settings
        self.configFactoryDefault()
        self.zeroGyroBiasNow()
        self.setYaw(startYaw)
        self.setStatusFramePeriod(PigeonIMU_StatusFrame.PigeonIMU_BiasedStatus_2_Gyro, 20)

        # Update the Sim Collection (if running in Simulator)
        if RobotBase.isSimulation():
            self.getSimCollection().setRawHeading( startYaw )

    def updateSysOutputs(self):
        """
        Update Network Table Logging
        """
        yprDegrees = self.getYawPitchRoll()[1]
        xyzDps = self.getRawGyro()[1]

        tbl = NetworkTableInstance.getDefault().getTable( "SysOutputs/SwerveDrive/Gyro" )
        tbl.putBoolean( "connected", self.getLastError() == ErrorCode.OK )
        tbl.putNumber( "rollPositionRad", units.degreesToRadians( yprDegrees[1] ) )
        tbl.putNumber( "pitchPositionRad", units.degreesToRadians( -yprDegrees[2] ) )
        tbl.putNumber( "yawPositionRad", units.degreesToRadians( yprDegrees[0] ) )
        tbl.putNumber( "rollVelocityRadPerSec", units.degreesToRadians( xyzDps[1] ) )
        tbl.putNumber( "pitchVelocityRadPerSec", units.degreesToRadians( -xyzDps[0] ) )
        tbl.putNumber( "yawVelocityRadPerSec", units.degreesToRadians( xyzDps[2] ) )