from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import DriverStation

from util import *
from .ClimberIO import ClimberIO

class Climber(Subsystem):
    # class ClimberPositions:
    #     bottom = 0.0
    #     top = 100

    def __init__(self, climber:ClimberIO):
        self.climber = climber
        self.climberInputs = climber.ClimberIOInputs()
        self.climberLogger = NetworkTableInstance.getDefault().getStructTopic( "/Climber", ClimberIO.ClimberIOInputs ).publish()
        self.climberMeasuredLogger = NetworkTableInstance.getDefault().getTable( "/Logging/Climber" )

        self.offline = NTTunableBoolean( "/DisableSubsystem/Climber", False, persistent=True )

    def periodic(self):
        # Logging
        self.climber.updateInputs( self.climberInputs )
        self.climberLogger.set( self.climberInputs )
        #NewLogger# Logger.getInstance().processInputs( "Climber", self.climberInputs )
        
        # Run Subsystem
        if DriverStation.isDisabled() or self.offline.get():
            self.stop()

        if False: #self.isCharacterizing.get():
            self.climber.runCharacterization( self.charSettingsVolts.get(), self.charSettingsRotation.get() )
        else:
             self.climber.upateLeft()
             self.climber.upateRight()

        # Post Run Logging
        # self.climberMeasuredLogger.putNumber( "Measured", self.climber.getVelocity() )
        # self.climberMeasuredLogger.putNumber( "Setpoint", self.climber.getSetpoint() )

    ## Start nifrengrioe functions
    def updateLeft(self):
        self.climber.updateLeft()
    def updateRight(self):
        self.climber.updateRight()

    def setBrakeMode(self, brake:bool) -> None:
        self.climber.setBrakeMode(brake)
    
    def getLPosition(self):
        return self.climber.getLPosition()
    def getRPosition(self):
        return self.climber.getRPosition()
    
    def setLPosition(self, position: int):
        self.climber.setLPosition(position)
    def setRPosition(self, position: int):
        self.climber.setRPosition(position)
    
    def moveLeftClimber(self, speed:float):
        self.climber.moveLeftClimber(speed)
    def moveRightClimber(self, speed:float):
        self.climber.moveRightClimber(speed)
    ## End ntrbno functions