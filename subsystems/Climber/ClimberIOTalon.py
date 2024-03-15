from phoenix5 import WPI_TalonSRX, FeedbackDevice, NeutralMode, ControlMode
from wpimath import applyDeadband
from wpilib import DigitalInput

from .ClimberIO import ClimberIO

from util import *

class ClimberIOTalon(ClimberIO):
    def __init__( self, motorId:int, sensorId:int, invert:bool = False ):
        # Tunable Settings
        self.extendRate = NTTunableFloat('/Config/Climber/ExtendRate', 10.0, updater=self.resetPid, persistent=True)
        self.climber_kP = NTTunableFloat('/Config/Climber/PID/kP', 0.0, updater=self.resetPid, persistent=True)
        self.climber_kI = NTTunableFloat('/Config/Climber/PID/kI', 0.0, updater=self.resetPid, persistent=True)
        self.climber_Iz = NTTunableFloat('/Config/Climber/PID/Izone', 0.0, updater=self.resetPid, persistent=True)
        self.climber_kD = NTTunableFloat('/Config/Climber/PID/kD', 0.0, updater=self.resetPid, persistent=True)
        self.climber_kF = NTTunableFloat('/Config/Climber/PID/kFF', 0.0, updater=self.resetPid, persistent=True)

        # Static Variables
        self.actualPosition = 0.0
        self.desiredPosition = 0.0

        # Left Motor
        self.climbMotor = WPI_TalonSRX( motorId )
        self.climbMotor.clearStickyFaults()
        self.climbMotor.configFactoryDefault()
        self.climbMotor.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative)
        self.climbMotor.setSensorPhase( False )
        self.climbMotor.setInverted( invert )
        self.climbMotor.setNeutralMode( NeutralMode.Brake )
        
        self.resetPid()

        # Left Limit Switch
        self.sensor = DigitalInput( sensorId )
        
    def updateInputs( self, inputs: ClimberIO.ClimberIOInputs ) -> None:
        #Left Motor
        inputs.motorAppliedVolts = self.climbMotor.getMotorOutputVoltage()
        inputs.motorCurrentAmps = self.climbMotor.getOutputCurrent()
        inputs.motorTempCelcius = self.climbMotor.getTemperature()
        inputs.motorPosition = self.climbMotor.getSelectedSensorPosition()
        inputs.motorVelocity = self.climbMotor.getSelectedSensorVelocity()
        inputs.sensor = self.sensor.get()

        self.actualPosition = inputs.motorPosition

    def resetPid(self):
        self.climbMotor.config_kP( 0, self.climber_kP.get(), 250 )
        self.climbMotor.config_kI( 0, self.climber_kI.get(), 250 )
        self.climbMotor.config_kD( 0, self.climber_kD.get(), 250 )
        self.climbMotor.config_kF( 0, self.climber_kF.get(), 250 )
        self.climbMotor.config_IntegralZone( 0, self.climber_Iz.get(), 250 )
        self.climbMotor.selectProfileSlot( 0, 0 )

    def run(self):
        if not self.sensor.get() and self.desiredPosition < 0.0:
            self.resetPosition( 0.0 )
            self.desiredPosition = 0.0
        
        self.climbMotor.set( ControlMode.Position, self.desiredPosition )
    
    def setBrake( self, brake:bool ) -> None:
        self.climbMotor.setNeutralMode( NeutralMode.Brake if brake else NeutralMode.Coast )
    
    def setPosition( self, position:float ):
        self.desiredPosition = position

    def getPosition(self) -> float:
        return self.actualPosition

    def getSetpoint(self) -> float:
        return self.desiredPosition
   
    def movePosition( self, speed:float ):
        speed = applyDeadband( speed, 0.04 )
        currentPos = self.getPosition()
        self.desiredPosition = currentPos[0] + ( speed * self.extendRate.get() )
    
    def resetPosition( self, position:float ):
        self.climbMotor.setSelectedSensorPosition( position, 0, 250 )

