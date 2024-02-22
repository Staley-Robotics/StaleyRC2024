from commands2 import Subsystem

from .ElevatorIO import ElevatorIO
from util import *

class Elevator(Subsystem):
    class ElevatorPositions:
        Bottom = NTTunableFloat( "/Config/ElevatorPositions/Bottom", 0.0, persistent=True )
        Amp = NTTunableFloat( "/Config/ElevatorPositions/Amp", 0.0, persistent=True )
        Climb = NTTunableFloat( "/Config/ElevatorPositions/Climb", 0.0, persistent=True )
        Trap = NTTunableFloat( "/Config/ElevatorPositions/Trap", 0.0, persistent=True )
        Top = NTTunableFloat( "/Config/ElevatorPositions/Top", 0.0, persistent=True )

    def __init__(self, elevator:ElevatorIO):
        pass

    def periodic(self):
        pass

    def setPosition(self, position) -> None: pass
    def movePosition(self, position) -> None: pass
    def atPosition(self) -> bool: return False