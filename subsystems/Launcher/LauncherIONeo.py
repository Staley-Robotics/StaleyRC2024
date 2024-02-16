from rev import *

from .LauncherIO import LauncherIO

class LauncherIONeo(LauncherIO):
    def __init__( self, leftCanId:int, rightCanId:int, sensorId:int ):
        # Static Variables
        self.actualVelocity = [ 0.0, 0.0 ]
        self.desiredVelocity = [ 0.0, 0.0 ]

        # Left Motor
        self.leftMotor = CANSparkMax( leftCanId, CANSparkMax.MotorType.kBrushless )
        self.leftMotor.clearFaults()
        self.leftMotor.restoreFactoryDefaults()
        self.leftMotor.setIdleMode( CANSparkMax.IdleMode.kCoast )
        self.leftMotor.setInverted( True )
        self.leftMotor.burnFlash()

        self.leftEncoder = self.leftMotor.getEncoder()
        
        # Right Motor
        self.rightMotor = CANSparkMax( rightCanId, CANSparkMax.MotorType.kBrushless )
        self.rightMotor.clearFaults()
        self.rightMotor.restoreFactoryDefaults()
        self.rightMotor.setIdleMode( CANSparkMax.IdleMode.kCoast )
        self.rightMotor.setInverted( False )
        self.rightMotor.burnFlash()

        self.rightEncoder = self.rightMotor.getEncoder()

    def updateInputs(self, inputs: LauncherIO.LauncherIOInputs) -> None:
        self.actualVelocity[0] = self.leftEncoder.getVelocity()
        inputs.leftAppliedVolts = self.leftMotor.getAppliedOutput() * self.leftMotor.getBusVoltage()
        inputs.leftCurrentAmps = self.leftMotor.getOutputCurrent()
        inputs.leftPosition = self.leftEncoder.getPosition()
        inputs.leftVelocity = self.actualVelocity[0]
        inputs.leftTempCelcius = self.leftMotor.getMotorTemperature()

        self.actualVelocity[1] = self.rightEncoder.getVelocity()
        inputs.rightAppliedVolts = self.rightMotor.getAppliedOutput() * self.rightMotor.getBusVoltage()
        inputs.rightCurrentAmps = self.rightMotor.getOutputCurrent()
        inputs.rightPosition = self.rightEncoder.getPosition()
        inputs.rightVelocity = self.actualVelocity[1]
        inputs.rightTempCelcius = self.rightMotor.getMotorTemperature()

        inputs.sensor = False

    def run(self):
        self.leftMotor.set( self.desiredVelocity[0] )
        self.rightMotor.set( self.desiredVelocity[1] )

    def setVelocity(self, leftVelocity:float, rightVelocity:float ):
        self.desiredVelocity = [ leftVelocity, rightVelocity ]

    def getVelocity(self):
        return self.actualVelocity
    
    def getSetpoint(self):
        return self.desiredVelocity