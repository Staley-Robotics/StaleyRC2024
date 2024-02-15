from wpilib import *

from phoenix5 import *
from phoenix5.sensors import CANCoder

from util import *
from subsystems import PivotIO
from ntcore import *

class PivotIOFalcon(PivotIO):
    """
    Subsystem to handle double flywheel note launcher
    """
    def __init__(self):
        super().__init__()

        self.desiredPos = 0.0
        self.actualPos = 0.0

        #Tunables
        self.pivotKP = NTTunableFloat('Pivot/PID_kP', 0.2, updater=lambda:..., persistent=True)
        self.pivotKI = NTTunableFloat('Pivot/PID_kI', 0.0, updater=lambda:..., persistent=True)
        self.pivotKD = NTTunableFloat('Pivot/PID_kD', 0.0, updater=lambda:..., persistent=True)
        self.pivotKFF = NTTunableFloat('Pivot/PID_kFF', 0.2, updater=lambda:..., persistent=True)

        # Motors
        self.motor = WPI_TalonFX(15)
        self.motor.clearStickyFaults()
        self.motor.configFactoryDefault()
        self.motor.setNeutralMode(NeutralMode.Brake)
        self.motor.setInverted(False)

        self.actualSpeed = NTTunableFloat('Pivot/Actual Speed', 0.0, persistent=False)
        self.pivotSpeedMult = NTTunableFloat('Pivot/Speed Mulitiplier', 0.05, persistent=False)

        # PID
    
    def set_speed(self, speed):
        self.actualSpeed.set(speed * self.pivotSpeedMult.get())

    def go_to_angle(self, angle:float=0):
        """
        points pivot toward :param angle: in degrees
        0 is straight forwards
        """
        #not so fancy pid stuf
    
    def set_speed(self, speed):
        """
        for open loop control of pivot
        :param speed: in range [-1,1], how fast motor should move -- limited by pivotSpeedMult
        """
        self.actualSpeed.set(speed * self.pivotSpeedMult.get())
    
    def updateInputs(self, inputs: PivotIO.PivotInputs):
        """
        you can read the name, and if you cant, then idk how you're reading this
        """
        #NOTE: not sure if funcs are correct
        inputs.motorTempCelsius = self.motor.getTemperature()
        inputs.motorVoltage = self.motor.getMotorOutputVoltage()
        inputs.motorCurrent = self.motor.getOutputCurrent()
        inputs.motorVelocity = self.motor.getSelectedSensorVelocity()
        
        inputs.motorPosition = self.motor.getSelectedSensorPosition() #sensor units?
        inputs.desiredMotorPosition = self.desiredPos
