from phoenix5 import WPI_TalonFX, NeutralMode, RemoteFeedbackDevice, FeedbackDevice, ControlMode
from phoenix5.sensors import WPI_CANCoder, SensorInitializationStrategy, AbsoluteSensorRange
from wpilib import RobotBase

from util import *
from .PivotIO import PivotIO 

class PivotIOFalcon(PivotIO):
    
    def __init__(self, motorId:int, encoderId:int, encoderOffset:float=0.0):
        # Tunable Settings
        pivotCanBus = NTTunableString( "/Config/Pivot/Falcon/Motor/CanBus", "rio", persistent=True )
        pivotInvert = NTTunableBoolean( "/Config/Pivot/Falcon/Motor/Invert", False, updater=lambda: self.pivotMotor.setInverted( pivotInvert.get() ), persistent=True )
        pivotPhase = NTTunableBoolean( "/Config/Pivot/Falcon/Motor/Phase", False, updater=lambda: self.pivotMotor.setSensorPhase( pivotPhase.get() ), persistent=True )
        encoderCanBus = NTTunableString( "/Config/Pivot/Falcon/Encoder/CanBus", "rio", persistent=True )
        encoderDirection = NTTunableBoolean( "/Config/Pivot/Falcon/Encoder/PositiveClockwise", True, updater=lambda: self.pivotEncoder.configSensorDirection( encoderDirection.get() ), persistent=True )

        # Tunables
        self.pivot_kP = NTTunableFloat('Pivot/PID_kP', 0.2, updater=self.resetPid, persistent=True)
        self.pivot_kI = NTTunableFloat('Pivot/PID_kI', 0.0, updater=self.resetPid, persistent=True)
        self.pivot_Iz = NTTunableFloat('Pivot/PID_Izone', 0.0, updater=self.resetPid, persistent=True)
        self.pivot_kD = NTTunableFloat('Pivot/PID_kD', 0.0, updater=self.resetPid, persistent=True)
        self.pivot_kF = NTTunableFloat('Pivot/PID_kFF', 0.0, updater=self.resetPid, persistent=True)

        # Encoder
        self.pivotEncoder = WPI_CANCoder( encoderId, encoderCanBus.get() )
        self.pivotEncoder.configFactoryDefault()
        self.pivotEncoder.configSensorInitializationStrategy( SensorInitializationStrategy.BootToZero )
        self.pivotEncoder.configAbsoluteSensorRange( AbsoluteSensorRange.Signed_PlusMinus180 )
        self.pivotEncoder.configSensorDirection( encoderDirection.get() )
        if not RobotBase.isSimulation():
            self.pivotEncoder.setPosition( self.pivotEncoder.getAbsolutePosition() - encoderOffset )
        
        # Motor
        self.pivotMotor = WPI_TalonFX( motorId, pivotCanBus.get() )
        self.pivotMotor.configFactoryDefault()
        self.pivotMotor.setSensorPhase( pivotPhase.get() )
        self.pivotMotor.setInverted( pivotInvert.get() )
        self.pivotMotor.setNeutralMode( NeutralMode.Coast )
        self.pivotMotor.configFeedbackNotContinuous( True )
        self.pivotMotor.configNeutralDeadband( 0.005 )
        self.resetPid()
        
        # Link Encoder to Motor
        self.pivotMotor.configRemoteFeedbackFilter( self.pivotEncoder, 0 )
        self.pivotMotor.configSelectedFeedbackSensor( RemoteFeedbackDevice.RemoteSensor0, 0  )
        self.pivotMotor.configSelectedFeedbackSensor( FeedbackDevice.None_, 1 )

        # Stored Positions
        self.actualPosition = self.pivotMotor.getSelectedSensorPosition()
        self.desiredPosition = self.actualPosition

    def updateInputs(self, inputs:PivotIO.PivotIOInputs):

        inputs.motorAppliedVolts = self.pivotMotor.getMotorOutputVoltage()
        inputs.motorCurrentAmps = self.pivotMotor.getOutputCurrent()
        inputs.motorPosition = self.pivotMotor.getSelectedSensorPosition()
        inputs.motorVelocity = self.pivotMotor.getSelectedSensorVelocity()
        inputs.motorTempCelcius = self.pivotMotor.getTemperature()

        inputs.encoderPositionAbs = self.pivotEncoder.getAbsolutePosition()
        inputs.encoderPositionRel = self.pivotEncoder.getPosition()
        inputs.encoderVelocity = self.pivotEncoder.getVelocity()

        self.actualPosition = inputs.encoderPositionRel


    def resetPid(self):
        self.pivotMotor.config_kP( 0, self.pivot_kP.get() )
        self.pivotMotor.config_kI( 0, self.pivot_kI.get() )
        self.pivotMotor.config_kD( 0, self.pivot_kD.get() )
        self.pivotMotor.config_kF( 0, self.pivot_kF.get() )
        self.pivotMotor.config_IntegralZone( 0, self.pivot_Iz.get() )

    def run(self):
        pos = self.desiredPosition / 360 * 4096
        self.pivotMotor.set( ControlMode.Position, pos )

    def setPosition(self, degrees:float) -> None:
        self.desiredPosition = degrees

    def getPosition(self) -> float:
        return self.actualPosition
    
    def atSetpoint(self, errorRange:float=0.0) -> bool:
        atPos = self.pivotMotor.getClosedLoopError() < errorRange
        return atPos
    
    def getSetpoint(self) -> float:
        return self.desiredPosition