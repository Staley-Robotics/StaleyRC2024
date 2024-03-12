from rev import *
from .LauncherIO import LauncherIO

from util import *

class LauncherIONeo(LauncherIO):
    def __init__( self, leftCanId:int, rightCanId:int, sensorId:int ):
        # Tunable Settings
        leftInvert = NTTunableBoolean( "/Config/Launcher/Neo/LeftInvert", False, updater=lambda: self.leftMotor.setInverted( leftInvert.get() ), persistent=True )
        rightInvert = NTTunableBoolean( "/Config/Launcher/Neo/RightInvert", True, updater=lambda: self.rightMotor.setInverted( rightInvert.get() ), persistent=True )

        self.launcher_kP = NTTunableFloat('/Config/Launcher/PID_kP', 1.0, updater=self.resetPid, persistent=True)
        self.launcher_kI = NTTunableFloat('/Config/Launcher/PID_kI', 0.0, updater=self.resetPid, persistent=True)
        self.launcher_Iz = NTTunableFloat('/Config/Launcher/PID_Izone', 0.0, updater=self.resetPid, persistent=True)
        self.launcher_kD = NTTunableFloat('/Config/Launcher/PID_kD', 0.0, updater=self.resetPid, persistent=True)
        self.launcher_kF = NTTunableFloat('/Config/Launcher/PID_kFF', 0.0, updater=self.resetPid, persistent=True)

        # Static Variables
        self.actualVelocity = [ 0.0, 0.0 ]
        self.desiredVelocity = [ 0.0, 0.0 ]

        # Left Motor
        self.leftMotor = CANSparkMax( leftCanId, CANSparkMax.MotorType.kBrushless )
        self.leftMotor.setCANTimeout(250)
        self.leftMotor.clearFaults()
        self.leftMotor.restoreFactoryDefaults()
        self.leftMotor.setInverted( leftInvert.get() )
        self.leftMotor.setIdleMode( CANSparkMax.IdleMode.kCoast )
        self.leftMotor.setSmartCurrentLimit( 30 )
        self.leftMotor.setClosedLoopRampRate( 0.05 )

        self.leftEncoder = self.leftMotor.getEncoder()
        self.leftPid = self.leftMotor.getPIDController()
        self.leftPid.setFeedbackDevice( self.leftEncoder )
        
        # Right Motor
        self.rightMotor = CANSparkMax( rightCanId, CANSparkMax.MotorType.kBrushless )
        self.rightMotor.setCANTimeout(250)
        self.rightMotor.clearFaults()
        self.rightMotor.restoreFactoryDefaults()
        self.rightMotor.setInverted( rightInvert.get() )
        self.rightMotor.setIdleMode( CANSparkMax.IdleMode.kCoast )
        self.rightMotor.setSmartCurrentLimit( 30 )
        self.rightMotor.setClosedLoopRampRate( 0.05 )

        self.rightEncoder = self.rightMotor.getEncoder()
        self.rightPid = self.rightMotor.getPIDController()
        self.rightPid.setFeedbackDevice( self.rightEncoder )

        # Set / Save PID
        self.resetPid()

        # Save Configurations to Motor Controllers
        self.leftMotor.burnFlash()
        self.leftMotor.setCANTimeout(0)
        self.rightMotor.burnFlash()
        self.rightMotor.setCANTimeout(0)

        # IR Sensor
        self.irSensor = wpilib.DigitalInput(sensorId)
        self.lastSensor = self.irSensor.get()
        self.sensorCount = 0

    def updateInputs(self, inputs: LauncherIO.LauncherIOInputs) -> None:
        v0 = self.leftEncoder.getVelocity()
        inputs.leftAppliedVolts = self.leftMotor.getAppliedOutput() * self.leftMotor.getBusVoltage()
        inputs.leftCurrentAmps = self.leftMotor.getOutputCurrent()
        inputs.leftPosition = self.leftEncoder.getPosition()
        inputs.leftVelocity = self.leftEncoder.getVelocity()
        inputs.leftTempCelcius = self.leftMotor.getMotorTemperature()

        v1 = self.rightEncoder.getVelocity()
        inputs.rightAppliedVolts = self.rightMotor.getAppliedOutput() * self.rightMotor.getBusVoltage()
        inputs.rightCurrentAmps = self.rightMotor.getOutputCurrent()
        inputs.rightPosition = self.rightEncoder.getPosition()
        inputs.rightVelocity = self.rightEncoder.getVelocity()
        inputs.rightTempCelcius = self.rightMotor.getMotorTemperature()

        self.actualVelocity = [ v0, v1 ]
        inputs.sensor = self.irSensor.get()

    def resetPid(self):
        self.leftPid.setP( self.launcher_kP.get(), 0 )
        self.leftPid.setI( self.launcher_kI.get(), 0 )
        self.leftPid.setD( self.launcher_kD.get(), 0 )
        self.leftPid.setFF( self.launcher_kF.get(), 0 )
        self.leftPid.setIZone( self.launcher_Iz.get(), 0 )

        self.rightPid.setP( self.launcher_kP.get(), 0 )
        self.rightPid.setI( self.launcher_kI.get(), 0 )
        self.rightPid.setD( self.launcher_kD.get(), 0 )
        self.rightPid.setFF( self.launcher_kF.get(), 0 )
        self.rightPid.setIZone( self.launcher_Iz.get(), 0 )

    def run(self):
        if self.desiredVelocity[0] == 0.0 and self.desiredVelocity[1] == 0.0:
            self.leftMotor.set( self.desiredVelocity[0] )
            self.rightMotor.set( self.desiredVelocity[1] )
        else:
            self.leftPid.setReference( self.desiredVelocity[0], CANSparkMax.ControlType.kVelocity, 0 )
            self.rightPid.setReference( self.desiredVelocity[1], CANSparkMax.ControlType.kVelocity, 0 )

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