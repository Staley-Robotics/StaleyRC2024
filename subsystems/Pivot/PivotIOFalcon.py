from phoenix5 import *
from phoenix5.sensors import *
from wpilib import RobotBase

from util import *
from .PivotIO import PivotIO 

class PivotIOFalcon(PivotIO):
    
    def __init__(self, motorId:int, encoderId:int, encoderOffset:float=0.0):
        # Tunables
        self.pivot_kP = NTTunableFloat('Pivot/PID_kP', 0.2, updater=self.resetPid)
        self.pivot_kI = NTTunableFloat('Pivot/PID_kI', 0.0, updater=self.resetPid)
        self.pivot_Iz = NTTunableFloat('Pivot/PID_Izone', 0.0, updater=self.resetPid)
        self.pivot_kD = NTTunableFloat('Pivot/PID_kD', 0.0, updater=self.resetPid)
        self.pivot_kF = NTTunableFloat('Pivot/PID_kFF', 0.2, updater=self.resetPid)

        # Encoder
        self.pivotEncoder = WPI_CANCoder( encoderId, "canivore" )
        self.pivotEncoder.configFactoryDefault()
        self.pivotEncoder.configSensorInitializationStrategy( SensorInitializationStrategy.BootToZero )
        self.pivotEncoder.configAbsoluteSensorRange( AbsoluteSensorRange.Unsigned_0_to_360 )
        self.pivotEncoder.configSensorDirection( False )
        if not RobotBase.isSimulation():
            self.pivotEncoder.setPosition( self.pivotEncoder.getAbsolutePosition() - encoderOffset )
        
        # Motor
        self.pivotMotor = WPI_TalonFX( motorId, "canivore" )
        self.pivotMotor.configFactoryDefault()
        self.pivotMotor.setSensorPhase( True )
        self.pivotMotor.setInverted( True )
        self.pivotMotor.setNeutralMode( NeutralMode.Brake )
        self.pivotMotor.configFeedbackNotContinuous( True )
        self.pivotMotor.configNeutralDeadband( 0.005 )
        self.resetPid()
        
        # Link Encoder to Motor
        self.pivotMotor.configRemoteFeedbackFilter( self.pivotEncoder )
        self.pivotMotor.configSelectedFeedbackSensor( RemoteFeedbackDevice.RemoteSensor0, 0  )
        self.pivotMotor.configSelectedFeedbackSensor( FeedbackDevice.None_, 1 )

        # Stored Positions
        self.actualPosition = self.pivotMotor.getSelectedSensorPosition()
        self.desiredPosition = self.actualPosition

    def updateInputs(self, inputs:PivotIO.PivotIOInputs):
        self.actualPosition = self.pivotMotor.getSelectedSensorPosition()

        inputs.motorAppliedVolts = self.pivotMotor.getMotorOutputVoltage()
        inputs.motorCurrentAmps =self.pivotMotor.getOutputCurrent()
        inputs.motorPosition = self.actualPosition
        inputs.motorVelocity = self.pivotMotor.getSelectedSensorVelocity()
        inputs.motorTempCelcius = self.pivotMotor.getTemperature()

        inputs.encoderPositionAbs = self.pivotEncoder.getAbsolutePosition()
        inputs.encoderPositionRel = self.pivotEncoder.getPosition()
        inputs.encoderVelocity = self.pivotEncoder.getVelocity()

    def resetPid(self):
        self.pivotMotor.config_kP( 0, self.pivot_kP.get() )
        self.pivotMotor.config_kI( 0, self.pivot_kI.get() )
        self.pivotMotor.config_kD( 0, self.pivot_kD.get() )
        self.pivotMotor.config_kF( 0, self.pivot_kF.get() )
        self.pivotMotor.config_IntegralZone( 0, self.pivot_Iz.get() )

    def run(self):
        self.pivotMotor.set( ControlMode.Position, self.desiredPosition )

    def setPosition(self, degrees:float) -> None:
        self.desiredPosition = degrees

    def getPosition(self) -> float:
        return self.actualPosition
    
    def atSetpoint(self, errorRange:float=0.0) -> bool:
        atPos = self.pivotMotor.getClosedLoopError() < errorRange
        return atPos
    
    def getSetpoint(self) -> float:
        return self.desiredPosition