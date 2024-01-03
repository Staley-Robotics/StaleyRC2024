from ntcore import *
from wpiutil import *

class RobotProperty(Sendable):
    _name:str = ""
    _value:bool = False

    def __init__(self, name, value):
        Sendable.__init__(self)
        self._name = name
        self._value = value
        pass

    def get(self) -> bool:
        return self._value
    
    def set(self, value:bool) -> None:
        self._value = value

    def update(self) -> None:
        self._builder.update()

    def initSendable(self, builder:SendableBuilder):
        builder.setSmartDashboardType( "RobotPreferences" )
        builder.addBooleanProperty( self._name, self.get, self.set )
        self._builder = builder