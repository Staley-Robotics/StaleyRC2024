from rev import *

from .LauncherIO import LauncherIO

from util import *

class LauncherIONeo(LauncherIO):
    def __init__( self, leftCanId:int, rightCanId:int, sensorId:int ):
        # Tunable Settings
        leftInvert = NTTunableBoolean( "/Config/Launcher/Neo/LeftInvert", False, updater=lambda: self.leftMotor.setInverted( leftInvert.get() ), persistent=True )
        rightInvert = NTTunableBoolean( "/Config/Launcher/Neo/RightInvert", True, updater=lambda: self.rightMotor.setInverted( rightInvert.get() ), persistent=False )

        # Static Variables
        self.actualVelocity = [ 0.0, 0.0 ]
        self.desiredVelocity = [ 0.0, 0.0 ]

        # Left Motor
        self.leftMotor = CANSparkMax( leftCanId, CANSparkMax.MotorType.kBrushless )
        self.leftMotor.clearFaults()
        self.leftMotor.restoreFactoryDefaults()
        self.leftMotor.setIdleMode( CANSparkMax.IdleMode.kCoast )
        self.leftMotor.setInverted( leftInvert.get() )
        self.leftMotor.burnFlash()

        self.leftEncoder = self.leftMotor.getEncoder()
        
        # Right Motor
        self.rightMotor = CANSparkMax( rightCanId, CANSparkMax.MotorType.kBrushless )
        self.rightMotor.clearFaults()
        self.rightMotor.restoreFactoryDefaults()
        self.rightMotor.setIdleMode( CANSparkMax.IdleMode.kCoast )
        self.rightMotor.setInverted( rightInvert.get() )
        self.rightMotor.burnFlash()

        self.rightEncoder = self.rightMotor.getEncoder()

        # IR Sensor
        self.irSensor = wpilib.DigitalInput(sensorId)
        self.lastSensor = self.irSensor.get()
        self.sensorCount = 0

    def updateInputs(self, inputs: LauncherIO.LauncherIOInputs) -> None:
        v0 = self.leftMotor.getAppliedOutput()
        inputs.leftAppliedVolts = v0 * self.leftMotor.getBusVoltage()
        inputs.leftCurrentAmps = self.leftMotor.getOutputCurrent()
        inputs.leftPosition = self.leftEncoder.getPosition()
        inputs.leftVelocity = self.leftEncoder.getVelocity()
        inputs.leftTempCelcius = self.leftMotor.getMotorTemperature()

        v1 = self.rightMotor.getAppliedOutput()
        inputs.rightAppliedVolts = v1 * self.rightMotor.getBusVoltage()
        inputs.rightCurrentAmps = self.rightMotor.getOutputCurrent()
        inputs.rightPosition = self.rightEncoder.getPosition()
        inputs.rightVelocity = self.rightEncoder.getVelocity()
        inputs.rightTempCelcius = self.rightMotor.getMotorTemperature()

        self.actualVelocity = [ v0, v1 ]
        inputs.sensor = self.irSensor.get()

    def run(self):
        self.leftMotor.set( self.desiredVelocity[0] )
        self.rightMotor.set( self.desiredVelocity[1] )

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