from phoenix5 import WPI_TalonFX, NeutralMode

from .IntakeIO import IntakeIO

from util import *

class IntakeIOFalcon(IntakeIO):
    def __init__(self, upperCanId:int, lowerCanId:int, sensorId:int ):
        # Tunable Settings
        upperCanBus = NTTunableString( "/Config/Intake/Falcon/UpperMotor/CanBus", "canivore1", persistent=False )
        upperInvert = NTTunableBoolean( "/Config/Intake/Falcon/UpperMotor/Invert", False, updater=lambda: self.upperMotor.setInverted( upperInvert.get() ), persistent=True )
        lowerCanBus = NTTunableString( "/Config/Intake/Falcon/LowerMotor/CanBus", "canivore1", persistent=False )
        lowerInvert = NTTunableBoolean( "/Config/Intake/Falcon/LowerMotor/Invert", False, updater=lambda: self.lowerMotor.setInverted( lowerInvert.get() ), persistent=True )

        # Static Variables
        self.actualVelocity = [ 0.0, 0.0 ]
        self.desiredVelocity = [ 0.0, 0.0 ]
        
        # Upper Motor
        self.upperMotor = WPI_TalonFX( upperCanId, upperCanBus.get() )
        self.upperMotor.clearStickyFaults()
        self.upperMotor.configFactoryDefault()
        self.upperMotor.setNeutralMode( NeutralMode.Coast )
        self.upperMotor.setInverted( upperInvert.get() )

        # Lower Motor
        self.lowerMotor = WPI_TalonFX( lowerCanId, lowerCanBus.get() )
        self.lowerMotor.clearStickyFaults()
        self.lowerMotor.configFactoryDefault()
        self.lowerMotor.setNeutralMode( NeutralMode.Coast )
        self.lowerMotor.setInverted( lowerInvert.get() )

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

    def getVelocity(self):# -> [float, float]:
        return self.actualVelocity
    
    def getSetpoint(self):# -> [float, float]:
        return self.desiredVelocity
    