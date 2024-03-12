from rev import *
from phoenix5 import *
from wpimath import applyDeadband

from .ClimberIO import ClimberIO

from util import *

class ClimberIOTalon(ClimberIO):
    def __init__( self, lMotorId:int, rMotorId:int ):
        # Tunable Settings
        lMotorInvert = NTTunableBoolean( "/Config/Climber/LeftTalon/Invert", True, updater=lambda: self.lClimbMotor.setInverted( lMotorInvert.get() ), persistent=True )
        rMotorInvert = NTTunableBoolean( "/Config/Climber/RightTalon/Invert", True, updater=lambda: self.rClimbMotor.setInverted( rMotorInvert.get() ), persistent=True )
        self.lExtendRate = NTTunableFloat( "/Config/Climber/LeftTalon/ExtendRate", 10.0, persistent=True )
        self.rExtendRate = NTTunableFloat( "/Config/Climber/RightTalon/ExtendRate", 10.0, persistent=True )

        # Tunables
        self.climber_kP = NTTunableFloat('/Config/Climber/PID/kP', 0.0, updater=self.resetPid, persistent=True)
        self.climber_kI = NTTunableFloat('/Config/Climber/PID/kI', 0.0, updater=self.resetPid, persistent=True)
        self.climber_Iz = NTTunableFloat('/Config/Climber/PID/Izone', 0.0, updater=self.resetPid, persistent=True)
        self.climber_kD = NTTunableFloat('/Config/Climber/PID/kD', 0.0, updater=self.resetPid, persistent=True)
        self.climber_kF = NTTunableFloat('/Config/Climber/PID/kFF', 0.0, updater=self.resetPid, persistent=True)

        # Static Variables
        self.actualPosition = [ 0.0, 0.0 ]
        self.desiredPosition = [ 0.0, 0.0 ]

        # Left Motor
        self.lClimbMotor = WPI_TalonSRX( lMotorId )
        self.lClimbMotor.clearStickyFaults()
        self.lClimbMotor.configFactoryDefault()
        self.lClimbMotor.setNeutralMode( NeutralMode.Brake )
        self.lClimbMotor.setInverted( lMotorInvert.get() )
        self.lClimbMotor.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative)
        
        #Right Motor
        self.rClimbMotor = WPI_TalonSRX( rMotorId )
        self.rClimbMotor.clearStickyFaults()
        self.rClimbMotor.configFactoryDefault()
        self.rClimbMotor.setNeutralMode( NeutralMode.Brake )
        self.rClimbMotor.setInverted( rMotorInvert.get() )
        self.rClimbMotor.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative)

        self.resetPid()
        
    def updateInputs( self, inputs: ClimberIO.ClimberIOInputs ) -> None:
        #Left Motor
        inputs.leftAppliedVolts = self.lClimbMotor.getMotorOutputVoltage()
        inputs.leftCurrentAmps = self.lClimbMotor.getOutputCurrent()
        inputs.leftTempCelcius = self.lClimbMotor.getTemperature()
        inputs.leftPosition = self.lClimbMotor.getSelectedSensorPosition()
        inputs.leftVelocity = self.lClimbMotor.getSelectedSensorVelocity()

        #Right Motor
        inputs.rightAppliedVolts = self.rClimbMotor.getMotorOutputVoltage()
        inputs.rightCurrentAmps = self.rClimbMotor.getOutputCurrent()
        inputs.rightTempCelcius = self.rClimbMotor.getTemperature()
        inputs.rightPosition = self.rClimbMotor.getSelectedSensorPosition()
        inputs.rightVelocity = self.rClimbMotor.getSelectedSensorVelocity()

        self.actualPosition = [ inputs.leftPosition, inputs.rightPosition ]

    def resetPid(self):
        self.lClimbMotor.config_kP( 0, self.climber_kP.get(), 250 )
        self.lClimbMotor.config_kI( 0, self.climber_kI.get(), 250 )
        self.lClimbMotor.config_kD( 0, self.climber_kD.get(), 250 )
        self.lClimbMotor.config_kF( 0, self.climber_kF.get(), 250 )
        self.lClimbMotor.config_IntegralZone( 0, self.climber_Iz.get(), 250 )

        self.rClimbMotor.config_kP( 0, self.climber_kP.get(), 250 )
        self.rClimbMotor.config_kI( 0, self.climber_kI.get(), 250 )
        self.rClimbMotor.config_kD( 0, self.climber_kD.get(), 250 )
        self.rClimbMotor.config_kF( 0, self.climber_kF.get(), 250 )
        self.rClimbMotor.config_IntegralZone( 0, self.climber_Iz.get(), 250 )

    def run(self):
        self.lClimbMotor.set( ControlMode.Position, self.desiredPosition[0] )
        self.rClimbMotor.set( ControlMode.Position, self.desiredPosition[1] )
    
    def setBrake( self, brake:bool ) -> None:
        self.lClimbMotor.setNeutralMode( NeutralMode.Brake if brake else NeutralMode.Coast )
        self.rClimbMotor.setNeutralMode( NeutralMode.Brake if brake else NeutralMode.Coast )
    
    def setPosition( self, leftPosition:float, rightPosition:float ):
        self.desiredLPosition = leftPosition
        self.desiredRPosition = rightPosition

    def getPosition(self) -> [float, float]:
        return self.actualPosition

    def getSetpoint(self) -> [float, float]:
        return self.desiredPosition, self.desiredPosition
   
    def movePosition( self, leftSpeed:float, rightSpeed:float ):
        leftSpeed = applyDeadband( leftSpeed, 0.04 )
        rightSpeed = applyDeadband( rightSpeed, 0.04 )
        currentPos = self.getPosition()
        self.desiredPosition = [
            currentPos[0] + ( leftSpeed * self.lExtendRate.get() ),
            currentPos[1] + ( rightSpeed * self.rExtendRate.get() )
        ]
    
    def resetPosition( self, position:float ):
        self.lClimbMotor.setSelectedSensorPosition( position, 0, 250 )
        self.rClimbMotor.setSelectedSensorPosition( position, 0, 250 )
