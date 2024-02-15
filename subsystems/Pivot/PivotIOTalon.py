from wpilib import *

from phoenix5 import *
from phoenix5.sensors import CANCoder

from util import *
from subsystems import Pivot
from ntcore import *

class PivotIOTalon(Pivot):
    """
    Subsystem to handle double flywheel note launcher
    """
    def __init__(self):
        super().__init__()
        #Tunables
        self.pivotKP = NTTunableFloat('Pivot/PID_kP', 0.2, updater=lambda:..., persistent=True)
        self.pivotKI = NTTunableFloat('Pivot/PID_kI', 0.0, updater=lambda:..., persistent=True)
        self.pivotKD = NTTunableFloat('Pivot/PID_kD', 0.0, updater=lambda:..., persistent=True)
        self.pivotKFF = NTTunableFloat('Pivot/PID_kFF', 0.2, updater=lambda:..., persistent=True)

        self.desiredPosition = NTTunableFloat('Pivot/Desired Position', 0.0)

        # Motors
        self.motor = WPI_TalonFX(15)
        self.motor.clearStickyFaults()
        self.motor.configFactoryDefault()
        self.motor.setNeutralMode(NeutralMode(2))
        self.motor.setInverted(False)
        #burn flash?

        # PID
        

        
        # Logging
        self.motorInputs = self.PivotInputs()
        self.ntMotorInputs = NetworkTableInstance.getDefault().getStructTopic('Pivot/Inputs', Pivot.PivotInputs).publish()

    def periodic(self) -> None:
        # Logging
        self.updateInputs(self.motorInputs)
        self.ntMotorInputs.set(self.motorInputs)

        # Run motor
        self.motor.set(self.actualSpeed.get())

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
    
    def updateInputs(self, inputs: Pivot.PivotInputs):
        """
        you can read the name, and if you cant, then idk how you're reading this
        """
        #NOTE: not sure if funcs are correct
        inputs.motorTempCelsius = self.motor.getTemperature()
        inputs.motorVoltage = self.motor.getMotorOutputVoltage()
        inputs.motorCurrent = self.motor.getOutputCurrent()
        inputs.motorVelocity = self.motor.getSelectedSensorVelocity()
        
        inputs.motorPosition = self.motor.getSelectedSensorPosition() #sensor units?
        inputs.desiredMotorPosition = self.desiredPosition.get()
