from phoenix5 import WPI_TalonFX, NeutralMode, RemoteFeedbackDevice, FeedbackDevice, ControlMode, SupplyCurrentLimitConfiguration, StatorCurrentLimitConfiguration
from phoenix5.sensors import WPI_CANCoder, SensorInitializationStrategy, AbsoluteSensorRange
from wpilib import RobotBase

from util import *
from .PivotIO import PivotIO 

class PivotIOFalcon(PivotIO):
    
    def __init__(self, motorId:int, encoderId:int, encoderOffset:float=0.0):
        # Tunable Settings
        # Tunables
        self.pivot_kP = NTTunableFloat('Pivot/PID_kP', 5, updater=self.resetPid, persistent=True)
        self.pivot_kI = NTTunableFloat('Pivot/PID_kI', 0.0, updater=self.resetPid, persistent=True)
        self.pivot_Iz = NTTunableFloat('Pivot/PID_Izone', 0.0, updater=self.resetPid, persistent=True)
        self.pivot_kD = NTTunableFloat('Pivot/PID_kD', 0.0, updater=self.resetPid, persistent=True)
        self.pivot_kF = NTTunableFloat('Pivot/PID_kFF', 0.0, updater=self.resetPid, persistent=True)

        # Encoder
        self.pivotEncoderOffset = encoderOffset
        self.pivotEncoder = WPI_CANCoder( encoderId, "canivore1" )
        self.pivotEncoder.configFactoryDefault( 250 )
        self.pivotEncoder.configSensorInitializationStrategy( SensorInitializationStrategy.BootToAbsolutePosition, 250 )
        self.pivotEncoder.configAbsoluteSensorRange( AbsoluteSensorRange.Signed_PlusMinus180, 250 )
        self.pivotEncoder.configSensorDirection( True, 250 )
        self.pivotEncoder.configMagnetOffset( encoderOffset, 250 )        

        # Motor
        self.pivotMotor = WPI_TalonFX( motorId, "canivore1" )
        self.pivotMotor.configFactoryDefault( 250 )
        self.pivotMotor.setSensorPhase( False )
        self.pivotMotor.setInverted( False )
        self.pivotMotor.setNeutralMode( NeutralMode.Coast )
        self.pivotMotor.configFeedbackNotContinuous( True, 250 )
        self.pivotMotor.configNeutralDeadband( 0.005, 250 )
        self.resetPid()
        
        # # Falcon Current Limit???
        # supplyCurrentCfg = SupplyCurrentLimitConfiguration( True, 40, 40, 1.0 )
        # self.pivotMotor.configSupplyCurrentLimit( supplyCurrentCfg, 250 )
        # statorCurrentCfg = StatorCurrentLimitConfiguration( True, 40, 40, 1.0 )
        # self.pivotMotor.configStatorCurrentLimit( statorCurrentCfg, 250 )
        
        # Link Encoder to Motor
        self.pivotMotor.configRemoteFeedbackFilter( self.pivotEncoder, 0, 250 )
        self.pivotMotor.configSelectedFeedbackSensor( RemoteFeedbackDevice.RemoteSensor0, 0, 250  )
        self.pivotMotor.configSelectedFeedbackSensor( FeedbackDevice.None_, 1, 250 )

        # Stored Positions
        self.actualPosition = self.pivotEncoder.getPosition()
        self.desiredPosition = self.actualPosition

    def updateInputs(self, inputs:PivotIO.PivotIOInputs):

        inputs.motorAppliedVolts = self.pivotMotor.getMotorOutputVoltage()
        inputs.motorCurrentAmps = self.pivotMotor.getOutputCurrent()
        inputs.motorPosition = self.pivotMotor.getSelectedSensorPosition()
        inputs.motorCurrentAmps = self.pivotMotor.getOutputCurrent()
        inputs.motorPosition = self.pivotMotor.getSelectedSensorPosition()
        inputs.motorVelocity = self.pivotMotor.getSelectedSensorVelocity()
        inputs.motorTempCelcius = self.pivotMotor.getTemperature()

        inputs.encoderPositionAbs = self.pivotEncoder.getAbsolutePosition()
        inputs.encoderPositionRel = self.pivotEncoder.getPosition()
        inputs.encoderVelocity = self.pivotEncoder.getVelocity()

        self.actualPosition = inputs.encoderPositionRel

    def resetPid(self):
        self.pivotMotor.config_kP( 0, self.pivot_kP.get(), 250 )
        self.pivotMotor.config_kI( 0, self.pivot_kI.get(), 250 )
        self.pivotMotor.config_kD( 0, self.pivot_kD.get(), 250 )
        self.pivotMotor.config_kF( 0, self.pivot_kF.get(), 250 )
        self.pivotMotor.config_IntegralZone( 0, self.pivot_Iz.get(), 250 )

    def run(self):
        pos = self.desiredPosition / 360 * 4096
        self.pivotMotor.set( ControlMode.Position, pos )

    def setPosition(self, degrees:float) -> None:
        self.desiredPosition = degrees

    def getPosition(self) -> float:
        return self.actualPosition
    
    # def atSetpoint(self, errorRange:float=0.0) -> bool:
    #     atPos = self.pivotMotor.getClosedLoopError() < errorRange
    #     return atPos
    
    def getSetpoint(self) -> float:
        return self.desiredPosition

    def syncEncoder(self) -> None:
        newPos = self.pivotEncoder.getAbsolutePosition()
        #if not RobotBase.isSimulation():
        #    newPos -= self.pivotEncoderOffset
        self.pivotEncoder.setPosition( newPos, 250 )
