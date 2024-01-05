from ctre import ErrorCode
from ctre.sensors import WPI_Pigeon2, PigeonIMU_StatusFrame
from ntcore import NetworkTableInstance
from wpilib import RobotBase
from wpimath import units

class CustomPigeon(WPI_Pigeon2):
    def __init__( self, deviceNumber:int, canbus:str = '', startYaw:float = 0.0 ):
        super().__init__( deviceNumber, canbus )

        self.configFactoryDefault()
        self.zeroGyroBiasNow()
        self.setYaw(startYaw)
        self.setStatusFramePeriod(PigeonIMU_StatusFrame.PigeonIMU_BiasedStatus_2_Gyro, 20)

        if RobotBase.isSimulation():
            self.getSimCollection().setRawHeading( startYaw )

    def updateLogs( self, tableName:str ):
        """
        Update Network Table Logging
        """
        yprDegrees = self.getYawPitchRoll()[1]
        xyzDps = self.getRawGyro()[1]

        tbl = NetworkTableInstance.getDefault().getTable(tableName)
        tbl.putBoolean( "connected", self.getLastError() == ErrorCode.OK )
        tbl.putNumber( "rollPositionRad", units.degreesToRadians( yprDegrees[1] ) )
        tbl.putNumber( "pitchPositionRad", units.degreesToRadians( -yprDegrees[2] ) )
        tbl.putNumber( "yawPositionRad", units.degreesToRadians( yprDegrees[0] ) )
        tbl.putNumber( "rollVelocityRadPerSec", units.degreesToRadians( xyzDps[1] ) )
        tbl.putNumber( "pitchVelocityRadPerSec", units.degreesToRadians( -xyzDps[0] ) )
        tbl.putNumber( "yawVelocityRadPerSec", units.degreesToRadians( xyzDps[2] ) )