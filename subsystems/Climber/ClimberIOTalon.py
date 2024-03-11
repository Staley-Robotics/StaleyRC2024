from rev import *
from phoenix5 import *

from .ClimberIO import ClimberIO

from util import *

class ClimberIOTalon(ClimberIO):
    def __init__(self, lMotorId:int, rMotorId:int):
        # Tunable Settings
        motorCanBus = NTTunableString( "/Config/Climber/CanBus", "canivore1", persistent=False)
        lMotorInvert = NTTunableBoolean( "/Config/Climber/LeftTalon/Invert", True, updater=lambda: self.lClimbMotor.setInverted( lMotorInvert.get() ), persistent=True )
        rMotorInvert = NTTunableBoolean( "/Config/Climber/RightTalon/Invert", True, updater=lambda: self.rClimbMotor.setInverted( rMotorInvert.get() ), persistent=True )

        # Tunables
        self.climber_kP = NTTunableFloat('Climber/PID_kP', 0.0, updater=self.resetPid, persistent=True)
        self.climber_kI = NTTunableFloat('Climber/PID_kI', 0.0, updater=self.resetPid, persistent=True)
        self.climber_Iz = NTTunableFloat('Climber/PID_Izone', 0.0, updater=self.resetPid, persistent=True)
        self.climber_kD = NTTunableFloat('Climber/PID_kD', 0.0, updater=self.resetPid, persistent=True)
        self.climber_kF = NTTunableFloat('Climber/PID_kFF', 0.0, updater=self.resetPid, persistent=True)

        # Static Variables
        self.actualLPosition = 0.0
        self.actualRPosition = 0.0
        self.desiredLPosition = 0.0
        self.desiredRPosition = 0.0

        self.rotationsPerSec = 0.0

        # Left Motor
        self.lClimbMotor = TalonSRX(lMotorId, motorCanBus.get())
        self.lClimbMotor.clearStickyFaults()
        self.lClimbMotor.configFactoryDefault()
        self.lClimbMotor.setNeutralMode( NeutralMode.Brake )
        self.lClimbMotor.setInverted( lMotorInvert.get() )
        self.lClimbMotor.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative)
        #Right Motor
        self.rClimbMotor = TalonSRX(rMotorId, motorCanBus.get())
        self.rClimbMotor.clearStickyFaults()
        self.rClimbMotor.configFactoryDefault()
        self.rClimbMotor.setNeutralMode( NeutralMode.Brake )
        self.rClimbMotor.setInverted( rMotorInvert.get() )
        self.rClimbMotor.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative)

        self.resetPid()
        
    def updateInputs(self, inputs: ClimberIO.ClimberIOInputs) -> None:
        #Left Motor
        inputs.lMotorAppliedVolts = self.lClimbMotor.getOutputCurrent() * self.lClimbMotor.getBusVoltage()
        inputs.lMotorCurrentAmps = self.lClimbMotor.getOutputCurrent()
        inputs.lMotorTempCelcius = self.lClimbMotor.getTemperature()

        self.actualLPosition = self.lClimbMotor.getSelectedSensorPosition()
        inputs.lMotorPosition = self.actualLPosition
        inputs.lMotorDesiredPosition = self.desiredLPosition

        #Right Motor
        inputs.rMotorAppliedVolts = self.rClimbMotor.getOutputCurrent() * self.rClimbMotor.getBusVoltage()
        inputs.rMotorCurrentAmps = self.rClimbMotor.getOutputCurrent()
        inputs.rMotorTempCelcius = self.rClimbMotor.getTemperature()

        self.actualRPosition = self.rClimbMotor.getSelectedSensorPosition()
        inputs.rMotorPosition = self.actualRPosition
        inputs.rMotorDesiredPosition = self.desiredRPosition

    def updateLeft(self) -> None:
        self.lClimbMotor.set( ControlMode.Position, self.desiredLPosition )
    def updateRight(self):
        self.rClimbMotor.set( ControlMode.Position, self.desiredRPosition )
    
    def setBrake(self, brake:bool) -> None:
        self.lClimbMotor.setNeutralMode( NeutralMode.Brake if brake else NeutralMode.Coast )
        self.rClimbMotor.setNeutralMode( NeutralMode.Brake if brake else NeutralMode.Coast )
    
    def getLPosition(self):
        return self.actualLPosition
    def getRPosition(self):
        return self.actualRPosition

    def setLPosition(self, position:int):
        self.desiredLPosition = position
    def setRPosition(self, position:int):
        self.desiredRPosition = position
    
    def moveLeftClimber(self, speed:float):
        self.setLPosition( self.getLPosition() + speed * self.rotationsPerSec )
    def moveRightClimber(self, speed:float):
        self.setRPosition( self.getRPosition() + speed * self.rotationsPerSec )
    
    def resetPid(self):
        self.lClimbMotor.config_kP( 0, self.climber_kP.get() )
        self.lClimbMotor.config_kI( 0, self.climber_kI.get() )
        self.lClimbMotor.config_kD( 0, self.climber_kD.get() )
        self.lClimbMotor.config_kF( 0, self.climber_kF.get() )
        self.lClimbMotor.config_IntegralZone( 0, self.climber_Iz.get() )

        self.rClimbMotor.config_kP( 0, self.climber_kP.get() )
        self.rClimbMotor.config_kI( 0, self.climber_kI.get() )
        self.rClimbMotor.config_kD( 0, self.climber_kD.get() )
        self.rClimbMotor.config_kF( 0, self.climber_kF.get() )
        self.rClimbMotor.config_IntegralZone( 0, self.climber_Iz.get() )