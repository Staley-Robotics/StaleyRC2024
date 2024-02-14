from phoenix5 import *

from .IntakeIO import IntakeIO

class IntakeIOFalcon(IntakeIO):
    def __init__(self, upperCanId, lowerCanId, sensorInId, sensorOutId ):
        # Static Variables
        self.actualVelocity = [ 0.0, 0.0 ]
        self.desiredVelocity = [ 0.0, 0.0 ]
        
        # Upper Motor
        self.upperMotor = WPI_TalonFX( upperCanId, "canivore" )
        self.upperMotor.clearStickyFaults()
        self.upperMotor.configFactoryDefault()
        self.upperMotor.setNeutralMode( NeutralMode.Coast )
        self.upperMotor.setInverted( True )

        # Lower Motor
        self.lowerMotor = WPI_TalonFX( lowerCanId, "canivore" )
        self.lowerMotor.clearStickyFaults()
        self.lowerMotor.configFactoryDefault()
        self.lowerMotor.setNeutralMode( NeutralMode.Coast )
        self.lowerMotor.setInverted( True )

    def updateInputs(self, inputs:IntakeIO.IntakeIOInputs):
        self.actualVelocity[0] = self.upperMotor.getSelectedSensorVelocity()
        inputs.upperAppliedVolts = self.upperMotor.getMotorOutputVoltage() # * self.leftMotor.getBusVoltage()
        inputs.upperCurrentAmps = self.upperMotor.getOutputCurrent()
        inputs.upperPosition = self.upperMotor.getSelectedSensorPosition()
        inputs.upperVelocity = self.actualVelocity[0]
        inputs.upperTempCelcius = self.upperMotor.getTemperature()

        self.actualVelocity[1] = self.lowerMotor.getSelectedSensorVelocity()
        inputs.lowerAppliedVolts = self.lowerMotor.getMotorOutputVoltage() # * self.rightMotor.getBusVoltage()
        inputs.lowerCurrentAmps = self.lowerMotor.getOutputCurrent()
        inputs.lowerPosition = self.lowerMotor.getSelectedSensorPosition()
        inputs.lowerVelocity = self.actualVelocity[1]
        inputs.lowerTempCelcius = self.lowerMotor.getTemperature()

        inputs.sensor = False

    def run(self):
        self.upperMotor.set( self.desiredVelocity[0] )
        self.lowerMotor.set( self.desiredVelocity[1] )

    def setBrake(self, brake:bool):
        mode = NeutralMode.Brake if brake else NeutralMode.Coast
        self.upperMotor.setNeutralMode( mode )
        self.lowerMotor.setNeutralMode( mode )

    def setVelocity(self, upperVelocity:float, lowerVelocity:float):
        self.desiredVelocity = [ upperVelocity, lowerVelocity ]

    def getVelocity(self) -> [float, float]:
        return self.actualVelocity
    
    def getSetpoint(self) -> [float, float]:
        return self.desiredVelocity
    