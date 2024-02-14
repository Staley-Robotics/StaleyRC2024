from wpilib import *

from phoenix5 import *
from phoenix5.sensors import CANCoder

from util import *
from subsystems import Pivot
from ntcore import *

class PivotTalon_FX(Pivot):
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

        # Motors
        self.motor = WPI_TalonFX(15)

        # PID
        self.encoder = CANCoder(10)
        # Idk im tired
        self.PID = PIDController(self.pivotKP.get(), self.pivotKI.get(), self.pivotKD.get())
        
        # Logging
        self.motorInputs = self.PivotInputs()
        self.ntMotorInputs = NetworkTableInstance.getDefault().getStructTopic('Pivot/Inputs', self.PivotInputs).publish()

    def periodic(self) -> None:
        # Logging
        self.updateInputs(self.motorInputs)
        self.ntMotorInputs.set(self.motorInputs)

        # Run motor
        self.motor.set(self.actualSpeed.get())

    def go_to(self, angle:float=0):
        """
        pivot towards angle
        """
        #make PID exist
    
    def set_speed(self, speed):
        self.actualSpeed.set(speed * self.pivotSpeedMult.get())
    
    def updateInputs(self, inputs: Pivot.PivotInputs):
        inputs.motorTempCelsius = self.motor.getTemperature()
