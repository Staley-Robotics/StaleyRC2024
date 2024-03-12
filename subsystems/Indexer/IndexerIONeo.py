from rev import *

from .IndexerIO import IndexerIO

from util import *

class IndexerIONeo(IndexerIO):
    def __init__(self, idxCanId:int, lowerSensorId:int, upperSensorId:int):
        # Tunable Settings
        motorInvert = NTTunableBoolean( "/Config/Indexer/Neo/Invert", True, updater=lambda: self.idxMotor.setInverted( motorInvert.get() ), persistent=True )

        # Static Variables
        self.actualVelocity = 0.0
        self.desiredVelocity = 0.0

        # Left Motor
        self.idxMotor = CANSparkMax( idxCanId, CANSparkMax.MotorType.kBrushless )
        self.idxMotor.clearFaults()
        self.idxMotor.restoreFactoryDefaults()
        self.idxMotor.setIdleMode( CANSparkMax.IdleMode.kCoast )
        self.idxMotor.setInverted( motorInvert.get() )
        self.idxMotor.enableVoltageCompensation( 12.0 )
        self.idxMotor.setSmartCurrentLimit( 20 )
        self.idxMotor.setClosedLoopRampRate( 0.05 )
        self.idxMotor.burnFlash()

        self.idxEncoder = self.idxMotor.getEncoder()

        # ir Sensors
        self.upperSensor = wpilib.DigitalInput( upperSensorId )
        self.lowerSensor = wpilib.DigitalInput( lowerSensorId )
        
    def updateInputs(self, inputs: IndexerIO.IndexerIOInputs) -> None:
        self.actualVelocity = self.idxEncoder.getVelocity()
        inputs.appliedVolts = self.idxMotor.getAppliedOutput() * self.idxMotor.getBusVoltage()
        inputs.currentAmps = self.idxMotor.getOutputCurrent()
        inputs.position = self.idxEncoder.getPosition()
        inputs.velocity = self.actualVelocity
        inputs.tempCelcius = self.idxMotor.getMotorTemperature()

        inputs.sensorHandoff = self.lowerSensor.get()
        inputs.sensorLaunch = self.upperSensor.get()

    def run(self) -> None:
        self.idxMotor.set( self.desiredVelocity )
    
    def setBrake(self, brake:bool) -> None:
        mode = CANSparkMax.IdleMode.kBrake if brake else CANSparkMax.IdleMode.kCoast
        self.idxMotor.setIdleMode( mode )

    def setVelocity(self, velocity: float) -> None:
        self.desiredVelocity = velocity
    
    def getVelocity(self) -> float:
        return self.actualVelocity
    
    def getSetpoint(self) -> float:
        return self.desiredVelocity

    def getUpperSensorIsBroken(self) -> bool:
        return not self.upperSensor.get()
    
    def getLowerSensorIsBroken(self) -> bool:
        return not self.lowerSensor.get()