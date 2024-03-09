from phoenix5 import *

from .LauncherIO import LauncherIO

from util import *

class LauncherIOFalcon(LauncherIO):
    def __init__( self, leftCanId:int, rightCanId:int, sensorId:int ):
        # Tunable Settings
        leftInvert = NTTunableBoolean( "/Config/Launcher/Falcon/LeftInvert", False, updater=lambda: self.leftMotor.setInverted( leftInvert.get() ), persistent=True )
        rightInvert = NTTunableBoolean( "/Config/Launcher/Falcon/RightInvert", True, updater=lambda: self.rightMotor.setInverted( rightInvert.get() ), persistent=True )
        leftCanBus = NTTunableString( "/Config/Launcher/Falcon/LeftCanBus", "canivore1", persistent=True )
        rightCanBus = NTTunableString( "/Config/Launcher/Falcon/RightCanBus", "canivore1", persistent=True )

        self.launcher_kP = NTTunableFloat('/Config/Launcher/Falcon/PID/kP', 1.0, updater=self.resetPid, persistent=True)
        self.launcher_kI = NTTunableFloat('/Config/Launcher/Falcon/PID/kI', 0.0, updater=self.resetPid, persistent=True)
        self.launcher_Iz = NTTunableFloat('/Config/Launcher/Falcon/PID/Izone', 0.0, updater=self.resetPid, persistent=True)
        self.launcher_kD = NTTunableFloat('/Config/Launcher/Falcon/PID/kD', 0.0, updater=self.resetPid, persistent=True)
        self.launcher_kF = NTTunableFloat('/Config/Launcher/Falcon/PID/kFF', 0.0, updater=self.resetPid, persistent=True)

        # Static Variables
        self.actualVelocity = [ 0.0, 0.0 ]
        self.desiredVelocity = [ 0.0, 0.0 ]

        # Left Motor
        self.leftMotor = WPI_TalonFX( leftCanId, leftCanBus.get() )
        self.leftMotor.clearStickyFaults( 250 )
        self.leftMotor.configFactoryDefault( 250 )
        self.leftMotor.setNeutralMode( NeutralMode.Coast )
        self.leftMotor.setInverted( leftInvert.get() )

        self.leftMotor.configVoltageCompSaturation( 12.0, 250 )
        self.leftMotor.enableVoltageCompensation( True )

        # Falcon Current Limit???
        #supplyCurrentCfg = SupplyCurrentLimitConfiguration( True, 40, 40, 1.0 )
        #self.leftMotor.configSupplyCurrentLimit( supplyCurrentCfg, 250 )
        #statorCurrentCfg = StatorCurrentLimitConfiguration( True, 40, 40, 1.0 )
        #self.leftMotor.configStatorCurrentLimit( statorCurrentCfg, 250 )

        # Right Motor
        self.rightMotor = WPI_TalonFX( rightCanId, rightCanBus.get() )
        self.rightMotor.clearStickyFaults( 250 )
        self.rightMotor.configFactoryDefault( 250 )
        self.rightMotor.setNeutralMode( NeutralMode.Coast )
        self.rightMotor.setInverted( rightInvert.get() )
        
        self.rightMotor.configVoltageCompSaturation( 12.0, 250 )
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
        v0 = self.leftMotor.getSelectedSensorVelocity()
        inputs.leftAppliedVolts = self.leftMotor.getMotorOutputVoltage() * self.leftMotor.getBusVoltage()
        inputs.leftCurrentAmps = self.leftMotor.getOutputCurrent()
        inputs.leftPosition = self.leftMotor.getSelectedSensorPosition()
        inputs.leftVelocity = v0
        inputs.leftTempCelcius = self.leftMotor.getTemperature()

        v1 = self.rightMotor.getSelectedSensorVelocity()
        inputs.rightAppliedVolts = self.rightMotor.getMotorOutputVoltage() * self.rightMotor.getBusVoltage()
        inputs.rightCurrentAmps = self.rightMotor.getOutputCurrent()
        inputs.rightPosition = self.rightMotor.getSelectedSensorPosition()
        inputs.rightVelocity = v1
        inputs.rightTempCelcius = self.rightMotor.getTemperature()

        self.actualVelocity = [ v0, v1 ]
        inputs.sensor = self.irSensor.get()

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

        if self.desiredVelocity[0] == 0.0 and self.desiredVelocity[1] == 0.0:
            controlMode = ControlMode.PercentOutput

        self.leftMotor.set( controlMode, self.desiredVelocity[0] )
        self.rightMotor.set( controlMode, self.desiredVelocity[1] )

    def setVelocity(self, leftVelocity:float, rightVelocity:float ):
        self.desiredVelocity = [ leftVelocity, rightVelocity ]

    def getVelocity(self):
        return self.actualVelocity
    
    def getSetpoint(self):
        return self.desiredVelocity
    
    def hasLaunched(self):
        currentSensor = self.irSensor.get()
        
        if currentSensor == self.lastSensor:
            if self.sensorCount == 2:
                self.sensorCount = 0
        else:
            if currentSensor:
                self.sensorCount += 1

        self.lastSensor = currentSensor
        return self.sensorCount == 2