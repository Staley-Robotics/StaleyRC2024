from threading import Thread

from wpilib import DigitalInput
from phoenix6.hardware import TalonFX
from phoenix6.configs import TalonFXConfiguration
from phoenix6.signals.spn_enums import NeutralModeValue, InvertedValue

from .IntakeIO import IntakeIO

from util import *

class IntakeIOFalcon(IntakeIO):
    def __init__(self, upperCanId:int, lowerCanId:int, upperSensorId:int, lowerSensorId:int = -1 ):
        # Static Variables
        self.actualVelocity = [ 0.0, 0.0 ]
        self.desiredVelocity = [ 0.0, 0.0 ]
        
        # Upper Motor
        self.upperMotor = TalonFX( upperCanId, "canivore1" )
        # self.upperMotor.clearStickyFaults()
        # self.upperMotor.configFactoryDefault()
        # self.upperMotor.setNeutralMode( NeutralMode.Coast )
        # self.upperMotor.setInverted( False )
        upperCfg = TalonFXConfiguration()
        upperCfg.motor_output.neutral_mode = NeutralModeValue.COAST
        upperCfg.motor_output.inverted = InvertedValue.COUNTER_CLOCKWISE_POSITIVE
        self.upperMotor.configurator.apply( upperCfg )

        # Lower Motor
        self.lowerMotor = TalonFX( lowerCanId, "canivore1" )
        # self.lowerMotor.clearStickyFaults()
        # self.lowerMotor.configFactoryDefault()
        # self.lowerMotor.setNeutralMode( NeutralMode.Coast )
        # self.lowerMotor.setInverted( False )
        lowerCfg = TalonFXConfiguration()
        lowerCfg.motor_output.neutral_mode = NeutralModeValue.COAST
        lowerCfg.motor_output.inverted = InvertedValue.COUNTER_CLOCKWISE_POSITIVE
        self.lowerMotor.configurator.apply( lowerCfg )

        # IR sensor
        self.irSensor = DigitalInput(upperSensorId)
        self.lowerSensor = DigitalInput(lowerSensorId)

    def updateInputs(self, inputs:IntakeIO.IntakeIOInputs):
        self.actualVelocity[0] = self.upperMotor.get_velocity().value #getSelectedSensorVelocity()
        inputs.upperAppliedVolts = self.upperMotor.get_motor_voltage().value #getMotorOutputVoltage()
        inputs.upperCurrentAmps = self.upperMotor.get_supply_current().value #getOutputCurrent()
        inputs.upperPosition = self.upperMotor.get_position().value #getSelectedSensorPosition()
        inputs.upperVelocity = self.actualVelocity[0]
        inputs.upperTempCelcius = self.upperMotor.get_device_temp().value #getTemperature()

        self.actualVelocity[1] = self.lowerMotor.get_velocity().value #getSelectedSensorVelocity()
        inputs.lowerAppliedVolts = self.lowerMotor.get_motor_voltage().value #getMotorOutputVoltage()
        inputs.lowerCurrentAmps = self.lowerMotor.get_supply_current().value #getOutputCurrent()
        inputs.lowerPosition = self.lowerMotor.get_position().value #getSelectedSensorPosition()
        inputs.lowerVelocity = self.actualVelocity[1]
        inputs.lowerTempCelcius = self.lowerMotor.get_device_temp().value #getTemperature()

        inputs.sensor = self.irSensor.get()

    def run(self):
        self.upperMotor.set( self.desiredVelocity[0] )
        self.lowerMotor.set( self.desiredVelocity[1] )

    def setBrake(self, brake:bool):
        # mode = NeutralMode.Brake if brake else NeutralMode.Coast
        # self.upperMotor.setNeutralMode( mode )
        # self.lowerMotor.setNeutralMode( mode )

        def setBrakeThread( brake:bool ):
            mode = NeutralModeValue.BRAKE if brake else NeutralModeValue.COAST
            self.upperMotor.setNeutralMode( mode )
            self.lowerMotor.setNeutralMode( mode )
    
        Thread( target = lambda: setBrakeThread( brake ) ).start()

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
    