from commands2 import Subsystem

from .ElevatorIO import ElevatorIO

class Elevator(Subsystem):
    class ElevatorPosition:
        Bottom = 0
        Amp = 3
        Climb = 0
        Trap = 8
        Top = 10

    def __init__(self, elevator:ElevatorIO):
        pass

    def periodic(self):
        pass