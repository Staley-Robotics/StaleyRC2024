from rev import *

from .IndexerIO import IndexerIO

from util import *

class IndexerIONeo(IndexerIO):
    def __init__(self, idxCanId:int, lowerSensorId:int, upperSensorId:int):
        # Tunable Settings
        motorInvert = NTTunableBoolean( "/Config/Indexer/Neo/Invert", False, updater=lambda: self.idxMotor.setInverted( motorInvert.get() ), persistent=True )

        # Static Variables
        self.actualVelocity = 0.0
        self.desiredVelocity = 0.0

        # Left Motor
        self.idxMotor = CANSparkMax( idxCanId, CANSparkMax.MotorType.kBrushless )
        self.idxMotor.clearFaults()
        self.idxMotor.restoreFactoryDefaults()
        self.idxMotor.setIdleMode( CANSparkMax.IdleMode.kCoast )
        self.idxMotor.setInverted( motorInvert.get() )
        self.idxMotor.burnFlash()

        self.idxEncoder = self.idxMotor.getEncoder()
        
    def updateInputs(self, inputs: IndexerIO.IndexerIOInputs) -> None:
        self.actualVelocity = self.idxEncoder.getVelocity()
        inputs.appliedVolts = self.idxMotor.getAppliedOutput() * self.idxMotor.getBusVoltage()
        inputs.currentAmps = self.idxMotor.getOutputCurrent()
        inputs.position = self.idxEncoder.getPosition()
        inputs.velocity = self.actualVelocity
        inputs.tempCelcius = self.idxMotor.getMotorTemperature()

        inputs.sensorHandoff = False
        inputs.sensorLaunch = False

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