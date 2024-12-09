from threading import Thread

from wpilib import DigitalInput
from rev import *

from .IndexerIO import IndexerIO

from util import *

class IndexerIONeo(IndexerIO):
    def __init__(self, idxCanId:int, lowerSensorId:int, upperSensorId:int):
        # Static Variables
        self.actualVelocity = 0.0
        self.desiredVelocity = 0.0

        # Left Motor
        self.idxMotor = SparkMax( idxCanId, SparkMax.MotorType.kBrushless )
        # self.idxMotor.clearFaults()
        # self.idxMotor.restoreFactoryDefaults()
        # self.idxMotor.setIdleMode( SparkMax.IdleMode.kCoast )
        # self.idxMotor.setInverted( True )
        # self.idxMotor.enableVoltageCompensation( 12.0 )
        # self.idxMotor.setSmartCurrentLimit( 20 )
        # self.idxMotor.setClosedLoopRampRate( 0.05 )
        # self.idxMotor.burnFlash()
        idxCfg = SparkMaxConfig()
        idxCfg = idxCfg.setIdleMode( SparkBaseConfig.IdleMode.kCoast )
        idxCfg = idxCfg.inverted( True )
        idxCfg = idxCfg.voltageCompensation( 12.0 )
        idxCfg = idxCfg.smartCurrentLimit( 20 )
        idxCfg = idxCfg.closedLoopRampRate( 0.05 )
        self.idxMotor.configure( idxCfg, SparkMax.ResetMode.kResetSafeParameters, SparkMax.PersistMode.kPersistParameters )

        self.idxEncoder = self.idxMotor.getEncoder()

        # ir Sensors
        self.upperSensor = DigitalInput( upperSensorId )
        self.lowerSensor = DigitalInput( lowerSensorId )
        
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
        def setBrakeThread(brake:bool) -> None:
            mode = SparkMaxConfig.IdleMode.kBrake if brake else SparkMaxConfig.IdleMode.kCoast
            cfg = SparkMaxConfig()
            cfg = cfg.setIdleMode( mode )
            self.idxMotor.configure( cfg, SparkMax.ResetMode.kNoResetSafeParameters, SparkMax.PersistMode.kNoPersistParameters )

        Thread( target = lambda: setBrakeThread(brake) ).start()

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