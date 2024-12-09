# from phoenix5 import WPI_TalonFX, NeutralMode, RemoteFeedbackDevice, FeedbackDevice, ControlMode, SupplyCurrentLimitConfiguration, StatorCurrentLimitConfiguration
# from phoenix5.sensors import WPI_CANCoder, SensorInitializationStrategy, AbsoluteSensorRange
from wpilib import RobotBase
from phoenix6.hardware import * # TalonFX, CANcoder
from phoenix6.configs import * # TalonFXConfiguration, CANcoderConfiguration
from phoenix6.controls import * # PositionDutyCycle
from phoenix6.signals.spn_enums import * #SensorDirectionValue, NeutralModeValue, InvertedValue

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
        self.pivotEncoder = CANcoder( encoderId, "canivore1" )
        #self.pivotEncoder.configFactoryDefault( 250 )
        #self.pivotEncoder.configSensorInitializationStrategy( SensorInitializationStrategy.BootToAbsolutePosition, 250 )
        #self.pivotEncoder.configAbsoluteSensorRange( AbsoluteSensorRange.Signed_PlusMinus180, 250 )
        #self.pivotEncoder.configSensorDirection( True, 250 )
        #self.pivotEncoder.configMagnetOffset( encoderOffset, 250 )
        pivotEncoderCfg = CANcoderConfiguration()
        pivotEncoderCfg.magnet_sensor.sensor_direction = SensorDirectionValue.COUNTER_CLOCKWISE_POSITIVE
        pivotEncoderCfg.magnet_sensor.absolute_sensor_discontinuity_point = 0.5
        pivotEncoderCfg.magnet_sensor.magnet_offset = encoderOffset / 360.0
        self.pivotEncoder.configurator.apply( pivotEncoderCfg )

        # Motor
        self.pivotMotor = TalonFX( motorId, "canivore1" )
        # self.pivotMotor.configFactoryDefault( 250 )
        # self.pivotMotor.setSensorPhase( False )
        # self.pivotMotor.setInverted( False )
        # self.pivotMotor.setNeutralMode( NeutralMode.Coast )
        # self.pivotMotor.configFeedbackNotContinuous( True, 250 )
        # self.pivotMotor.configNeutralDeadband( 0.005, 250 )
        pivotMotorCfg = TalonFXConfiguration()
        pivotMotorCfg.motor_output.neutral_mode = NeutralModeValue.COAST
        pivotMotorCfg.motor_output.inverted = InvertedValue.COUNTER_CLOCKWISE_POSITIVE
        pivotMotorCfg.motor_output.duty_cycle_neutral_deadband = 0.005
        self.pivotMotor.configurator.apply( pivotMotorCfg )
        self.resetPid()
        
        # # Falcon Current Limit???
        # supplyCurrentCfg = SupplyCurrentLimitConfiguration( True, 40, 40, 1.0 )
        # self.pivotMotor.configSupplyCurrentLimit( supplyCurrentCfg, 250 )
        # statorCurrentCfg = StatorCurrentLimitConfiguration( True, 40, 40, 1.0 )
        # self.pivotMotor.configStatorCurrentLimit( statorCurrentCfg, 250 )
        
        # Link Encoder to Motor
        # self.pivotMotor.configRemoteFeedbackFilter( self.pivotEncoder, 0, 250 )
        # self.pivotMotor.configSelectedFeedbackSensor( RemoteFeedbackDevice.RemoteSensor0, 0, 250  )
        # self.pivotMotor.configSelectedFeedbackSensor( FeedbackDevice.None_, 1, 250 )
        pivotMotorFbCfg = FeedbackConfigs()
        pivotMotorFbCfg.feedback_remote_sensor_id = encoderId
        self.pivotMotor.configurator.apply( pivotMotorFbCfg )

        # Stored Positions
        self.actualPosition = self.pivotEncoder.get_position().value #getPosition()
        self.desiredPosition = self.actualPosition

    def updateInputs(self, inputs:PivotIO.PivotIOInputs):

        inputs.motorAppliedVolts = self.pivotMotor.get_motor_voltage().value #getMotorOutputVoltage()
        inputs.motorCurrentAmps = self.pivotMotor.get_supply_current().value #getOutputCurrent()
        inputs.motorPosition = self.pivotMotor.get_rotor_position().value #getSelectedSensorPosition()
        inputs.motorVelocity = self.pivotMotor.get_rotor_velocity().value #getSelectedSensorVelocity()
        inputs.motorTempCelcius = self.pivotMotor.get_device_temp().value #getTemperature()

        inputs.encoderPositionAbs = self.pivotEncoder.get_absolute_position().value #getAbsolutePosition()
        inputs.encoderPositionRel = self.pivotEncoder.get_position().value #getPosition()
        inputs.encoderVelocity = self.pivotEncoder.get_velocity().value #getVelocity()

        self.actualPosition = inputs.encoderPositionRel

    def resetPid(self):
        # self.pivotMotor.config_kP( 0, self.pivot_kP.get(), 250 )
        # self.pivotMotor.config_kI( 0, self.pivot_kI.get(), 250 )
        # self.pivotMotor.config_kD( 0, self.pivot_kD.get(), 250 )
        # self.pivotMotor.config_kF( 0, self.pivot_kF.get(), 250 )
        # self.pivotMotor.config_IntegralZone( 0, self.pivot_Iz.get(), 250 )
        slot0Cfg = Slot0Configs()
        slot0Cfg.k_p = self.pivot_kP.get()
        slot0Cfg.k_i = self.pivot_kI.get()
        slot0Cfg.k_d = self.pivot_kD.get()
        slot0Cfg.k_s = self.pivot_kF.get()
        self.pivotMotor.configurator.apply( slot0Cfg )

    def run(self):
        # pos = self.desiredPosition / 360 * 4096
        # self.pivotMotor.set( ControlMode.Position, pos )
        pos = self.desiredPosition / 360
        self.pivotMotor.set_control( PositionDutyCycle(pos) )

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
        newPos = self.pivotEncoder.get_absolute_position().value #getAbsolutePosition()
        #if not RobotBase.isSimulation():
        #    newPos -= self.pivotEncoderOffset
        self.pivotEncoder.set_position( newPos ) #setPosition( newPos, 250 )
