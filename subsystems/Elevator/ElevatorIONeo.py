from phoenix5 import WPI_TalonFX, NeutralMode, RemoteFeedbackDevice, FeedbackDevice, ControlMode
from phoenix5.sensors import WPI_CANCoder, SensorInitializationStrategy, AbsoluteSensorRange
from wpilib import RobotBase

from util import *
from .ElevatorIO import ElevatorIO 

class ElevatorIONeo(ElevatorIO):
    
    def __init__(self, lMotorId:int, rMotorId:int):
        # Tunable Settings
        elevatorCanBus = NTTunableString( "/Config/Elevator/Falcon/Motor/CanBus", "canivore1", persistent=False )
        elevatorLMotorInvert = NTTunableBoolean( "/Config/Elevator/Falcon/lMotor/Invert", False, updater=lambda: self.elevatorMotor.setLMotorInverted( elevatorLMotorInvert.get() ), persistent=True )
        elevatorRMotorInvert = NTTunableBoolean( "/Config/Elevator/Falcon/rMotor/Phase", False, updater=lambda: self.elevatorMotor.setInverted( elevatorPhase.get() ), persistent=True )

        # Tunables
        self.elevator_kP = NTTunableFloat('Elevator/PID_kP', 5, updater=self.resetPid, persistent=True)
        self.elevator_kI = NTTunableFloat('Elevator/PID_kI', 0.0, updater=self.resetPid, persistent=True)
        self.elevator_Iz = NTTunableFloat('Elevator/PID_Izone', 0.0, updater=self.resetPid, persistent=True)
        self.elevator_kD = NTTunableFloat('Elevator/PID_kD', 0.0, updater=self.resetPid, persistent=True)
        self.elevator_kF = NTTunableFloat('Elevator/PID_kFF', 0.0, updater=self.resetPid, persistent=True)
        
        # Left Motor
        self.lMotor = WPI_TalonFX( lMotorId, elevatorCanBus.get() )
        self.lMotor.configFactoryDefault()
        self.lMotor.setInverted( elevatorLMotorInvert.get() )
        self.lMotor.setNeutralMode( NeutralMode.Coast )
        self.lMotor.configFeedbackNotContinuous( True )
        self.lMotor.configNeutralDeadband( 0.005 )
        # Right Motor
        self.rMotor = WPI_TalonFX( rMotorId, elevatorCanBus.get() )
        self.rMotor.configFactoryDefault()
        self.rMotor.setInverted( elevatorLMotorInvert.get() )
        self.rMotor.setNeutralMode( NeutralMode.Coast )
        self.rMotor.configFeedbackNotContinuous( True )
        self.rMotor.configNeutralDeadband( 0.005 )
        self.resetPid()

        # Stored Positions
        self.actualPosition = self.elevatorEncoder.getPosition()
        self.desiredPosition = self.actualPosition

    def updateInputs(self, inputs:ElevatorIO.ElevatorIOInputs):

        inputs.lMotorAppliedVolts = self.lMotor.getMotorOutputVoltage()
        inputs.lMotorCurrentAmps = self.lMotor.getOutputCurrent()
        inputs.lMotorPosition = self.lMotor.getSelectedSensorPosition()
        inputs.lMotorCurrentAmps = self.lMotor.getOutputCurrent()
        inputs.lMotorPosition = self.lMotor.getSelectedSensorPosition()
        inputs.lMotorVelocity = self.lMotor.getSelectedSensorVelocity()
        inputs.lMotorTempCelcius = self.lMotor.getTemperature()

        inputs.rMotorAppliedVolts = self.rMotor.getMotorOutputVoltage()
        inputs.rMotorCurrentAmps = self.rMotor.getOutputCurrent()
        inputs.rMotorPosition = self.rMotor.getSelectedSensorPosition()
        inputs.rMotorCurrentAmps = self.rMotor.getOutputCurrent()
        inputs.rMotorPosition = self.rMotor.getSelectedSensorPosition()
        inputs.rMotorVelocity = self.rMotor.getSelectedSensorVelocity()
        inputs.rMotorTempCelcius = self.rMotor.getTemperature()

    def resetPid(self):
        self.rMotor.config_kP( 0, self.elevator_kP.get() )
        self.rMotor.config_kI( 0, self.elevator_kI.get() )
        self.rMotor.config_kD( 0, self.elevator_kD.get() )
        self.rMotor.config_kF( 0, self.elevator_kF.get() )
        self.rMotor.config_IntegralZone( 0, self.elevator_Iz.get() )

    def run(self):
        pos = self.desiredPosition / 360 * 4096
        self.elevatorMotor.set( ControlMode.Position, pos )
        pos = self.desiredPosition / 360 * 4096
        self.elevatorMotor.set( ControlMode.Position, pos )

    def setPosition(self, degrees:float) -> None:
        self.desiredPosition = degrees

    def getPosition(self) -> float:
        return self.actualPosition
    
    def atSetpoint(self, errorRange:float=0.0) -> bool:
        atPos = self.elevatorMotor.getClosedLoopError() < errorRange
        return atPos
    
    def getSetpoint(self) -> float:
        return self.desiredPosition