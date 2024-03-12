from phoenix5 import *

from .LauncherIO import LauncherIO

from util import *

class LauncherIOFalcon(LauncherIO):
    def __init__( self, leftCanId:int, rightCanId:int, sensorId:int ):
        # Tunable Settings
        leftInvert = NTTunableBoolean( "/Config/Launcher/Falcon/LeftInvert", False, updater=lambda: self.leftMotor.setInverted( leftInvert.get() ), persistent=False )
        rightInvert = NTTunableBoolean( "/Config/Launcher/Falcon/RightInvert", True, updater=lambda: self.rightMotor.setInverted( rightInvert.get() ), persistent=False )
        leftCanBus = NTTunableString( "/Config/Launcher/Falcon/LeftCanBus", "canivore1", persistent=False )
        rightCanBus = NTTunableString( "/Config/Launcher/Falcon/RightCanBus", "canivore1", persistent=False )

        self.launcher_kP = NTTunableFloat('/Config/Launcher/Falcon/PID/kP', 1.0, updater=self.resetPid, persistent=True)
        self.launcher_kI = NTTunableFloat('/Config/Launcher/Falcon/PID/kI', 0.0, updater=self.resetPid, persistent=True)
        self.launcher_Iz = NTTunableFloat('/Config/Launcher/Falcon/PID/Izone', 0.0, updater=self.resetPid, persistent=True)
        self.launcher_kD = NTTunableFloat('/Config/Launcher/Falcon/PID/kD', 0.0, updater=self.resetPid, persistent=True)
        self.launcher_kF = NTTunableFloat('/Config/Launcher/Falcon/PID/kFF', 0.0, updater=self.resetPid, persistent=True)

        # Static Variables
        self.actualVelocity = [ 0.0, 0.0 ]
        self.desiredVelocity = [ 0.0, 0.0 ]

        # Left Motor
        self.leftMotor = WPI_TalonFX( leftCanId, "canivore1" )
        self.leftMotor.clearStickyFaults( 250 )
        self.leftMotor.configFactoryDefault( 250 )
        self.leftMotor.setNeutralMode( NeutralMode.Coast )
        self.leftMotor.setInverted( False )

        self.leftMotor.configVoltageCompSaturation( 11.0, 250 )
        self.leftMotor.enableVoltageCompensation( True )

        # Falcon Current Limit???
        #supplyCurrentCfg = SupplyCurrentLimitConfiguration( True, 40, 40, 1.0 )
        #self.leftMotor.configSupplyCurrentLimit( supplyCurrentCfg, 250 )
        #statorCurrentCfg = StatorCurrentLimitConfiguration( True, 40, 40, 1.0 )
        #self.leftMotor.configStatorCurrentLimit( statorCurrentCfg, 250 )

        # Right Motor
        self.rightMotor = WPI_TalonFX( rightCanId, "canivore1" )
        self.rightMotor.clearStickyFaults( 250 )
        self.rightMotor.configFactoryDefault( 250 )
        self.rightMotor.setNeutralMode( NeutralMode.Coast )
        self.rightMotor.setInverted( True )
        
        self.rightMotor.configVoltageCompSaturation( 11.0, 250 )
        self.rightMotor.enableVoltageCompensation( True )

        # Falcon Current Limit???
        #supplyCurrentCfg = SupplyCurrentLimitConfiguration( True, 40, 40, 1.0 )
        #self.rightMotor.configSupplyCurrentLimit( supplyCurrentCfg, 250 )
        #statorCurrentCfg = StatorCurrentLimitConfiguration( True, 40, 40, 1.0 )
        #self.rightMotor.configStatorCurrentLimit( statorCurrentCfg, 250 )

        # Set / Save PID
        self.resetPid()

        # IR Sensor
        self.irSensor = wpilib.DigitalInput(sensorId)
        self.lastSensor = self.irSensor.get()
        self.sensorCount = 0

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

    def run(self):
        controlMode = ControlMode.Velocity

        if self.lastSensor != self.irSensor.get():
            self.lastSensor = self.irSensor.get()
            self.sensorCount += 1

        if self.desiredVelocity[0] == 0.0 and self.desiredVelocity[1] == 0.0:
            self.sensorCount = 0
            controlMode = ControlMode.PercentOutput

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
        return self.sensorCount >= 2