from wpilib.simulation import FlywheelSim
from wpimath.system.plant import DCMotor

from .IndexerIO import IndexerIO

class IndexerIOSim(IndexerIO):
    def __init__(self):
        self.motor = FlywheelSim( DCMotor.NEO(1), 1, 0.004 )

        self.brake = False
        self.volts = 0.0
        self.velocity = 0.0
        self.position = 0.0
        self.setpoint = 0.0

    def updateInputs(self, inputs:IndexerIO.IndexerIOInputs) -> None:
        # Update Motor
        self.motor.update( 0.02 )

        # Update Position
        self.velocity = self.motor.getAngularVelocity()
        self.position += self.velocity * 0.02

        # Save Inputs
        inputs.appliedVolts = self.volts
        inputs.currentAmps = self.motor.getCurrentDraw()
        inputs.position = self.position 
        inputs.velocity = self.velocity
        inputs.tempCelcius = 0

    def run(self) -> None:
        self.volts = min(max( self.getSetpoint() * 12.0, -12.0 ), 12.0)
        self.motor.setInputVoltage( self.volts )

    def setBrake(self, brake:bool) -> None:
        self.brake = brake

    def setVelocity(self, velocity:float) -> None:
        self.setpoint = velocity

    def getVelocity(self) -> float:
        return self.velocity

    def atSetpoint(self) -> bool:
        return ( self.getSetpoint() == self.getVelocity() )
    
    def getSetpoint(self) -> bool:
        return self.setpoint
