from wpilib.simulation import FlywheelSim
from wpimath.system.plant import DCMotor

from .IntakeIO import IntakeIO

class IntakeIOSim(IntakeIO):
    def __init__(self):
        self.uMotor = FlywheelSim( DCMotor.falcon500(1), 1, 0.004 )
        self.lMotor = FlywheelSim( DCMotor.falcon500(1), 1, 0.004 )

        self.brake = False
        self.setpoint = 0.0

        self.uVolts = 0.0
        self.uVelocity = 0.0
        self.uPosition = 0.0

        self.lVolts = 0.0
        self.lVelocity = 0.0
        self.lPosition = 0.0

    def updateInputs(self, inputs:IntakeIO.IntakeIOInputs) -> None:
        # Update Motor
        self.uMotor.update( 0.02 )
        self.lMotor.update( 0.02 )

        # Update Velocity / Position
        self.uVelocity = self.uMotor.getAngularVelocity()
        self.lVelocity = self.lMotor.getAngularVelocity()
        self.uPosition += self.uVelocity * 0.02
        self.lPosition += self.lVelocity * 0.02

        # Save Inputs
        inputs.lowerPosition = self.lPosition
        inputs.lowerVelocity = self.lVelocity
        inputs.lowerAppliedVolts = self.lVolts
        inputs.lowerCurrentAmps = self.lMotor.getCurrentDraw()
        inputs.lowerTempCelcius = 0

        inputs.upperPosition = self.uPosition
        inputs.upperVelocity = self.uVelocity
        inputs.upperAppliedVolts = self.uVolts
        inputs.upperCurrentAmps = self.uMotor.getCurrentDraw()
        inputs.upperTempCelcius = 0

        inputs.sensor = False

    def run(self) -> None:
        volts = min(max( self.getSetpoint() * 12.0, -12.0 ), 12.0)
        self.uVolts = volts
        self.lVolts = volts
        self.uMotor.setInputVoltage( self.uVolts )
        self.lMotor.setInputVoltage( self.lVolts )

    def setBrake(self, brake:bool) -> None:
        self.brake = brake

    def setVelocity(self, velocity:float) -> None:
        self.setpoint = float(velocity)

    def getVelocity(self) -> float:
        return ( self.uVelocity + self.lVelocity ) / 2

    def atSetpoint(self) -> bool:
        return ( self.getSetpoint() == self.getVelocity() )
    
    def getSetpoint(self) -> float:
        return self.setpoint
