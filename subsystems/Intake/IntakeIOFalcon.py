from phoenix5 import WPI_TalonFX, NeutralMode

from .IntakeIO import IntakeIO

from util import *

class IntakeIOFalcon(IntakeIO):
    def __init__(self, upperCanId:int, lowerCanId:int, upperSensorId:int, lowerSensorId:int = -1 ):
        # Static Variables
        self.actualVelocity = [ 0.0, 0.0 ]
        self.desiredVelocity = [ 0.0, 0.0 ]
        
        # Upper Motor
        self.upperMotor = WPI_TalonFX( upperCanId, "canivore1" )
        self.upperMotor.clearStickyFaults()
        self.upperMotor.configFactoryDefault()
        self.upperMotor.setNeutralMode( NeutralMode.Coast )
        self.upperMotor.setInverted( False )

        # Lower Motor
        self.lowerMotor = WPI_TalonFX( lowerCanId, "canivore1" )
        self.lowerMotor.clearStickyFaults()
        self.lowerMotor.configFactoryDefault()
        self.lowerMotor.setNeutralMode( NeutralMode.Coast )
        self.lowerMotor.setInverted( False )

        # IR sensor
        self.irSensor = wpilib.DigitalInput(upperSensorId)
        self.lowerSensor = wpilib.DigitalInput(lowerSensorId)

    def updateInputs(self, inputs:IntakeIO.IntakeIOInputs):
        self.actualVelocity[0] = self.upperMotor.getSelectedSensorVelocity()
        inputs.upperAppliedVolts = self.upperMotor.getMotorOutputVoltage()
        inputs.upperCurrentAmps = self.upperMotor.getOutputCurrent()
        inputs.upperPosition = self.upperMotor.getSelectedSensorPosition()
        inputs.upperVelocity = self.actualVelocity[0]
        inputs.upperTempCelcius = self.upperMotor.getTemperature()

        self.actualVelocity[1] = self.lowerMotor.getSelectedSensorVelocity()
        inputs.lowerAppliedVolts = self.lowerMotor.getMotorOutputVoltage()
        inputs.lowerCurrentAmps = self.lowerMotor.getOutputCurrent()
        inputs.lowerPosition = self.lowerMotor.getSelectedSensorPosition()
        inputs.lowerVelocity = self.actualVelocity[1]
        inputs.lowerTempCelcius = self.lowerMotor.getTemperature()

        inputs.sensor = self.irSensor.get()

    def run(self):
        self.upperMotor.set( self.desiredVelocity[0] )
        self.lowerMotor.set( self.desiredVelocity[1] )

    def setBrake(self, brake:bool):
        mode = NeutralMode.Brake if brake else NeutralMode.Coast
        self.upperMotor.setNeutralMode( mode )
        self.lowerMotor.setNeutralMode( mode )

    def setVelocity(self, upperVelocity:float, lowerVelocity:float):
        self.desiredVelocity = [ upperVelocity, lowerVelocity ]

    def getVelocity(self):# -> [float, float]:
        return self.actualVelocity
    
    def getSetpoint(self):# -> [float, float]:
        return self.desiredVelocity

    def getSensorIsBroken(self) -> bool:
        #inverts bc i think backwards apparently
        return not self.irSensor.get()
    
    def foundNote(self) -> bool:
        return not self.lowerSensor.get()
    