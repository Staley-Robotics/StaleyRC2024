from wpilib import DigitalInput
from phoenix5 import *

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
        self.leftMotor = WPI_TalonFX( leftCanId, "canivore1" )
        self.leftMotor.clearStickyFaults( 250 )
        self.leftMotor.configFactoryDefault( 250 )
        self.leftMotor.setInverted( False )

        # Falcon Current Limit???
        #supplyCurrentCfg = SupplyCurrentLimitConfiguration( True, 40, 40, 1.0 )
        #self.leftMotor.configSupplyCurrentLimit( supplyCurrentCfg, 250 )
        #statorCurrentCfg = StatorCurrentLimitConfiguration( True, 40, 40, 1.0 )
        #self.leftMotor.configStatorCurrentLimit( statorCurrentCfg, 250 )

        # Right Motor
        self.rightMotor = WPI_TalonFX( rightCanId, "canivore1" )
        self.rightMotor.clearStickyFaults( 250 )
        self.rightMotor.configFactoryDefault( 250 )
        self.rightMotor.setInverted( True )

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
        inputs.leftAppliedVolts = self.leftMotor.getMotorOutputVoltage()
        inputs.leftCurrentAmps = self.leftMotor.getOutputCurrent()
        inputs.leftPosition = self.leftMotor.getSelectedSensorPosition()
        inputs.leftVelocity = self.leftMotor.getSelectedSensorVelocity()
        inputs.leftTempCelcius = self.leftMotor.getTemperature()

        inputs.rightAppliedVolts = self.rightMotor.getMotorOutputVoltage()
        inputs.rightCurrentAmps = self.rightMotor.getOutputCurrent()
        inputs.rightPosition = self.rightMotor.getSelectedSensorPosition()
        inputs.rightVelocity = self.rightMotor.getSelectedSensorVelocity()
        inputs.rightTempCelcius = self.rightMotor.getTemperature()

        inputs.sensor = self.irSensor.get()

        self.actualVelocity = [ inputs.leftVelocity, inputs.rightVelocity ]

    def resetPid(self):
        self.leftMotor.config_kP( 0, self.launcher_kP.get(), 250 )
        self.leftMotor.config_kI( 0, self.launcher_kI.get(), 250 )
        self.leftMotor.config_kD( 0, self.launcher_kD.get(), 250 )
        self.leftMotor.config_kF( 0, self.launcher_kF.get(), 250 )
        self.leftMotor.config_IntegralZone( 0, self.launcher_Iz.get(), 250 )

        self.rightMotor.config_kP( 0, self.launcher_kP.get(), 250 )
        self.rightMotor.config_kI( 0, self.launcher_kI.get(), 250 )
        self.rightMotor.config_kD( 0, self.launcher_kD.get(), 250 )
        self.rightMotor.config_kF( 0, self.launcher_kF.get(), 250 )
        self.rightMotor.config_IntegralZone( 0, self.launcher_Iz.get(), 250 )

    def setBrake(self, brake:bool):
        mode = NeutralMode.Brake if brake else NeutralMode.Coast
        self.leftMotor.setNeutralMode( mode )
        self.rightMotor.setNeutralMode( mode )

    def updateVoltageComp(self):
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
        controlMode = ControlMode.Velocity
        if self.desiredVelocity[0] == 0.0 and self.desiredVelocity[1] == 0.0:
            controlMode = ControlMode.PercentOutput

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
        self.leftMotor.set( controlMode, self.desiredVelocity[0] )
        self.rightMotor.set( controlMode, self.desiredVelocity[1] )

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