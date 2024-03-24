from phoenix5 import WPI_TalonSRX, FeedbackDevice, NeutralMode, ControlMode
from wpimath import applyDeadband
from wpilib import DigitalInput

from .ClimberIO import ClimberIO

from util import *

class ClimberIOTalon(ClimberIO):
    def __init__( self, motorId:int, topSensorId:int, bottomSensorId:int, invert:bool = False ):
        # Tunable Settings
        self.extendRate = NTTunableFloat('/Config/Climber/ExtendRate', 10.0, updater=self.resetPid, persistent=True)
        self.climber_kP = NTTunableFloat('/Config/Climber/PID/kP', 1.0, updater=self.resetPid, persistent=True)
        self.climber_kI = NTTunableFloat('/Config/Climber/PID/kI', 0.0, updater=self.resetPid, persistent=True)
        self.climber_Iz = NTTunableFloat('/Config/Climber/PID/Izone', 0.0, updater=self.resetPid, persistent=True)
        self.climber_kD = NTTunableFloat('/Config/Climber/PID/kD', 0.0, updater=self.resetPid, persistent=True)
        self.climber_kF = NTTunableFloat('/Config/Climber/PID/kFF', 0.0, updater=self.resetPid, persistent=True)

        # Static Variables
        self.actualRate = 0.0
        self.desiredRate = 0.0

        # Left Motor
        self.climbMotor = WPI_TalonSRX( motorId )
        self.climbMotor.clearStickyFaults()
        self.climbMotor.configFactoryDefault()
        self.climbMotor.setSensorPhase( False )
        self.climbMotor.setInverted( invert )
        self.climbMotor.setNeutralMode( NeutralMode.Brake )

        # Limit Switches
        self.topSensor = DigitalInput( topSensorId )
        self.bottomSensor = DigitalInput( bottomSensorId )
        
    def updateInputs( self, inputs: ClimberIO.ClimberIOInputs ) -> None:
        #Left Motor
        inputs.motorAppliedVolts = self.climbMotor.getMotorOutputVoltage()
        inputs.motorCurrentAmps = self.climbMotor.getOutputCurrent()
        inputs.motorTempCelcius = self.climbMotor.getTemperature()
        inputs.motorPosition = self.climbMotor.getSelectedSensorPosition()
        inputs.motorVelocity = self.climbMotor.getSelectedSensorVelocity()
        inputs.sensorBottom = self.bottomSensor.get()
        inputs.sensorTop = self.topSensor.get()

        self.actualRate = self.climbMotor.getMotorOutputPercent()

    def run(self):
        if self.atTop() and self.desiredRate > 0.0:
            self.desiredRate = 0.0
        if self.atBottom() and self.desiredRate < 0.0:
            self.desiredRate = 0.0
        
        self.climbMotor.set( ControlMode.PercentOutput, self.desiredRate )
    
    def setBrake( self, brake:bool ) -> None:
        self.climbMotor.setNeutralMode( NeutralMode.Brake if brake else NeutralMode.Coast )
    
    def setRate( self, rate:float ):
        self.desiredRate = rate

    def getRate(self) -> float:
        return self.actualRate
    
    def getSetpoint(self) -> float:
        return self.desiredRate
    
    def atTop(self) -> bool:
        return not self.topSensor.get()
    
    def atBottom(self) -> bool:
        return not self.bottomSensor.get()