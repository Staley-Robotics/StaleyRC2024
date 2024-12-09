from threading import Thread

from wpilib import DigitalInput
from phoenix6.hardware import TalonFX
from phoenix6.configs import TalonFXConfiguration, Slot0Configs, VoltageConfigs
from phoenix6.controls import * #DutyCycleOut, VelocityDutyCycle
from phoenix6.signals.spn_enums import NeutralModeValue, InvertedValue

from .LauncherIO import LauncherIO

from util import *

class LauncherIOFalcon(LauncherIO):
    def __init__( self, leftCanId:int, rightCanId:int, sensorId:int ):
        # Tunable Settings
        self.launcher_kP = NTTunableFloat('/Config/Launcher/Falcon/PID/kP', 0.20, updater=self.resetPid, persistent=True)
        self.launcher_kI = NTTunableFloat('/Config/Launcher/Falcon/PID/kI', 0.0, updater=self.resetPid, persistent=True)
        self.launcher_Iz = NTTunableFloat('/Config/Launcher/Falcon/PID/Izone', 0.0, updater=self.resetPid, persistent=True)
        self.launcher_kD = NTTunableFloat('/Config/Launcher/Falcon/PID/kD', 0.0, updater=self.resetPid, persistent=True)
        self.launcher_kF = NTTunableFloat('/Config/Launcher/Falcon/PID/kFF', 0.067, updater=self.resetPid, persistent=True)
        self.brakeMode = NTTunableBoolean('/Config/Launcher/Falcon/BrakeMode', True, updater=lambda: self.setBrake( self.brakeMode.get() ), persistent=True)
        self.voltageComp = NTTunableFloat('/Config/Launcher/Falcon/VoltageComp', 9.0, updater=self.updateVoltageComp, persistent=True)

        # Static Variables
        self.actualVelocity = [ 0.0, 0.0 ]
        self.desiredVelocity = [ 0.0, 0.0 ]

        # Left Motor
        self.leftMotor = TalonFX( leftCanId, "canivore1" )
        # self.leftMotor.clearStickyFaults( 250 )
        # self.leftMotor.configFactoryDefault( 250 )
        # self.leftMotor.setInverted( False )
        leftCfg = TalonFXConfiguration()
        leftCfg.motor_output.inverted = InvertedValue.COUNTER_CLOCKWISE_POSITIVE
        self.leftMotor.configurator.apply( leftCfg )

        # Falcon Current Limit???
        #supplyCurrentCfg = SupplyCurrentLimitConfiguration( True, 40, 40, 1.0 )
        #self.leftMotor.configSupplyCurrentLimit( supplyCurrentCfg, 250 )
        #statorCurrentCfg = StatorCurrentLimitConfiguration( True, 40, 40, 1.0 )
        #self.leftMotor.configStatorCurrentLimit( statorCurrentCfg, 250 )

        # Right Motor
        self.rightMotor = TalonFX( rightCanId, "canivore1" )
        # self.rightMotor.clearStickyFaults( 250 )
        # self.rightMotor.configFactoryDefault( 250 )
        # self.rightMotor.setInverted( True )
        rightCfg = TalonFXConfiguration()
        rightCfg.motor_output.inverted = InvertedValue.CLOCKWISE_POSITIVE
        self.rightMotor.configurator.apply( rightCfg )

        self.setBrake( self.brakeMode.get() )
        self.updateVoltageComp()

        # Falcon Current Limit???
        #supplyCurrentCfg = SupplyCurrentLimitConfiguration( True, 40, 40, 1.0 )
        #self.rightMotor.configSupplyCurrentLimit( supplyCurrentCfg, 250 )
        #statorCurrentCfg = StatorCurrentLimitConfiguration( True, 40, 40, 1.0 )
        #self.rightMotor.configStatorCurrentLimit( statorCurrentCfg, 250 )

        # Set / Save PID
        self.resetPid()

        # IR Sensor
        self.irSensor = DigitalInput(sensorId)
        self.lastSensor = self.irSensor.get()
        self.sensorCount = 0
        self.sensorDetected = False

    def updateInputs(self, inputs: LauncherIO.LauncherIOInputs) -> None:
        inputs.leftAppliedVolts = self.leftMotor.get_motor_voltage().value #getMotorOutputVoltage()
        inputs.leftCurrentAmps = self.leftMotor.get_supply_current().value #getOutputCurrent()
        inputs.leftPosition = self.leftMotor.get_position().value #getSelectedSensorPosition()
        inputs.leftVelocity = self.leftMotor.get_velocity().value #getSelectedSensorVelocity()
        inputs.leftTempCelcius = self.leftMotor.get_device_temp().value #getTemperature()

        inputs.rightAppliedVolts = self.rightMotor.get_motor_voltage().value #getMotorOutputVoltage()
        inputs.rightCurrentAmps = self.rightMotor.get_supply_current().value #getOutputCurrent()
        inputs.rightPosition = self.rightMotor.get_position().value #getSelectedSensorPosition()
        inputs.rightVelocity = self.rightMotor.get_velocity().value #getSelectedSensorVelocity()
        inputs.rightTempCelcius = self.rightMotor.get_device_temp().value #getTemperature()

        inputs.sensor = self.irSensor.get()

        self.actualVelocity = [ inputs.leftVelocity, inputs.rightVelocity ]

    def resetPid(self):
        # self.leftMotor.config_kP( 0, self.launcher_kP.get(), 250 )
        # self.leftMotor.config_kI( 0, self.launcher_kI.get(), 250 )
        # self.leftMotor.config_kD( 0, self.launcher_kD.get(), 250 )
        # self.leftMotor.config_kF( 0, self.launcher_kF.get(), 250 )
        # self.leftMotor.config_IntegralZone( 0, self.launcher_Iz.get(), 250 )

        # self.rightMotor.config_kP( 0, self.launcher_kP.get(), 250 )
        # self.rightMotor.config_kI( 0, self.launcher_kI.get(), 250 )
        # self.rightMotor.config_kD( 0, self.launcher_kD.get(), 250 )
        # self.rightMotor.config_kF( 0, self.launcher_kF.get(), 250 )
        # self.rightMotor.config_IntegralZone( 0, self.launcher_Iz.get(), 250 )

        slot0Cfg = Slot0Configs()
        slot0Cfg.k_p = self.launcher_kP.get() #self.leftMotor.config_kP( 0, self.launcher_kP.get(), 250 )
        slot0Cfg.k_i = self.launcher_kI.get() #self.leftMotor.config_kI( 0, self.launcher_kI.get(), 250 )
        slot0Cfg.k_d = self.launcher_kD.get() #self.leftMotor.config_kD( 0, self.launcher_kD.get(), 250 )
        slot0Cfg.k_v = self.launcher_kF.get() #self.leftMotor.config_kF( 0, self.launcher_kF.get(), 250 )
        self.leftMotor.configurator.apply( slot0Cfg )
        self.rightMotor.configurator.apply( slot0Cfg )

    def setBrake(self, brake:bool):
        # mode = NeutralMode.Brake if brake else NeutralMode.Coast
        # self.leftMotor.setNeutralMode( mode )
        # self.rightMotor.setNeutralMode( mode )

        def setBrakeThread(brake:bool):
            mode = NeutralModeValue.BRAKE if brake else NeutralModeValue.COAST
            self.leftMotor.setNeutralMode( mode )
            self.rightMotor.setNeutralMode( mode )

        Thread( target = lambda: setBrakeThread(brake) ).start()

    def updateVoltageComp(self):
        return 
        value = self.voltageComp.get()
        if value != abs( value ):
            self.voltageComp.set( abs(value) )
        elif value == 0.0:
            self.leftMotor.enableVoltageCompensation( False )
            self.rightMotor.enableVoltageCompensation( False )
        else:
            self.leftMotor.configVoltageCompSaturation( value, 250 )
            self.leftMotor.enableVoltageCompensation( True )
            self.rightMotor.configVoltageCompSaturation( value, 250 )
            self.rightMotor.enableVoltageCompensation( True )


    def run(self):
        # Control Mode
        # controlMode = ControlMode.Velocity
        # if self.desiredVelocity[0] == 0.0 and self.desiredVelocity[1] == 0.0:
        #     controlMode = ControlMode.PercentOutput

        # Launch Sensor Detection
        if self.desiredVelocity[0] == 0.0 and self.desiredVelocity[1] == 0.0:
            pass
            #self.sensorCount = 0
        elif self.lastSensor != self.irSensor.get():
            self.sensorCount += 1
            if self.sensorCount % 2 == 0:
                self.sensorDetected = True
            else:
                self.sensorDetected = False
        self.lastSensor = self.irSensor.get()

        # Set Motor
        # self.leftMotor.set( controlMode, self.desiredVelocity[0] )
        # self.rightMotor.set( controlMode, self.desiredVelocity[1] )
        outLeft = VelocityDutyCycle( self.desiredVelocity[0] ) if self.desiredVelocity[0] == 0.0 else DutyCycleOut( 0.0 )
        outRight = VelocityDutyCycle( self.desiredVelocity[1] ) if self.desiredVelocity[1] == 0.0 else DutyCycleOut( 0.0 )
        
        self.leftMotor.set_control( outLeft )
        self.rightMotor.set_control( outRight )

    def getSensorCount(self) -> int:
        return self.sensorCount

    def setVelocity(self, leftVelocity:float, rightVelocity:float ):
        self.desiredVelocity = [ leftVelocity, rightVelocity ]

    def getVelocity(self):
        return self.actualVelocity
    
    def getSetpoint(self):
        return self.desiredVelocity
    
    def hasLaunched(self):
        if self.sensorDetected and self.sensorCount % 2 == 0:
            self.sensorDetected = False
            return True
        #return self.sensorCount >= 2