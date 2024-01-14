import typing
from enum import Enum

import commands2
from wpilib import Timer
from wpimath.kinematics import ChassisSpeeds

import commands
import sequences
from subsystems import SwerveDrive
from util import *

class DriveCharacterization(commands2.Command):
    
    class Stage(Enum):
        kNotStarted = 0
        kStatic = 1
        kMaxAngularVelocity = 2
        kMaxVelocity = 3
        kComplete = 4

    charEnabled = NTTunableBoolean( "/Characterize/Enabled", False )
    charMOI = NTTunableFloat( "/Characterize/SwerveDrive/moiVolts", 0.0 )
    charMaxVelocity = NTTunableFloat( "/Characterize/SwerveDrive/maxStr8Velocity", 0.0 )
    charMaxAccel = NTTunableFloat( "/Characterize/SwerveDrive/maxStr8Accel", 0.0 )
    charMaxAngularVelocity = NTTunableFloat( "/Characterize/SwerveDrive/maxAngularVelocity", 0.0 )
    charMaxAngularAccel = NTTunableFloat( "/Characterize/SwerveDrive/maxAngularAccel", 0.0 )

    rampVoltsPerSec = 0.05

    def __init__( self,
                 driveTrain:commands2.Subsystem,
                 forward:bool,
                 startDelay:float
                ):
        super().__init__()
        self.addRequirements( driveTrain )

        self.myTimer:Timer = Timer()
        self.driveTrain:SwerveDrive = driveTrain
        self.forward:bool = forward
        self.startDelay:float = startDelay
        self.myStage:DriveCharacterization.Stage = DriveCharacterization.Stage.kNotStarted

        self.volts:float = 0.0
        self.lastCspeeds = ChassisSpeeds()

    def initialize(self):
        self.myStage == DriveCharacterization.Stage.kNotStarted
        self.charEnabled.set(True)
        self.volts = 0.0
        self.lastCspeeds = ChassisSpeeds()
        self.myTimer.reset()
        self.myTimer.start()
        return super().initialize()
    
    def execute(self):
        print( self.myStage, round(self.myTimer.get(),2), self.volts ) 
        if ( self.myTimer.get() < self.startDelay ):
            self.volts = 0.0
        else:
            cSpeeds:ChassisSpeeds = self.driveTrain.getChassisSpeeds()        
            match self.myStage:
                case DriveCharacterization.Stage.kNotStarted:
                    self.myStage = DriveCharacterization.Stage.kStatic
                    self.myTimer.reset()
                case DriveCharacterization.Stage.kStatic: 
                    if round(abs(cSpeeds.vx),2) != 0.0:
                        self.myStage = DriveCharacterization.Stage.kMaxVelocity
                        self.myTimer.reset()
                        self.volts = 0.0
                    else:
                        self.volts = (self.myTimer.get() - self.startDelay) * self.rampVoltsPerSec * (1.0 if self.forward else -1.0)
                        self.charMOI.set( self.volts )
                case DriveCharacterization.Stage.kMaxVelocity:
                    if round(self.lastCspeeds.vx,2) == round(cSpeeds.vx,2) and abs(round(cSpeeds.vx,2)) >= 0.01:
                        self.myStage = DriveCharacterization.Stage.kMaxAngularVelocity
                        self.myTimer.reset()
                        self.volts = 0.0
                    else:
                        self.volts = 12.0
                        self.charMaxVelocity.set( abs(round(cSpeeds.vx,3)) )
                        self.charMaxAccel.set( abs(round(cSpeeds.vx,3)) / (self.myTimer.get() - self.startDelay) )
                        self.lastCspeeds = cSpeeds
                case DriveCharacterization.Stage.kMaxAngularVelocity:
                    if cSpeeds.omega != 0.0 and round(cSpeeds.omega,2) == round(self.lastCspeeds.omega,2):
                        self.myStage = DriveCharacterization.Stage.kComplete
                        self.myTimer.reset()
                        self.volts = 0
                    else:
                        self.volts = 12.0
                        self.charMaxAngularVelocity.set( abs(round(cSpeeds.omega,3)) )
                        self.charMaxAngularAccel.set( abs(round(cSpeeds.omega,3)) / (self.myTimer.get() - self.startDelay) )
                        self.lastCspeeds = cSpeeds
                case DriveCharacterization.Stage.kComplete:
                    self.volts = 0
                case _:
                    raise Exception( "DriveCharacterization: Unknown Stage Occured.")
            
        self.driveTrain.runCharacterization(
            self.volts,
            self.myStage == DriveCharacterization.Stage.kMaxAngularVelocity
        )

        return super().execute()
    
    def end(self, interrupted: bool):
        self.myTimer.stop()
        self.charEnabled.set(False)
        self.driveTrain.stop()
        return super().end(interrupted)
    
    def isFinished(self) -> bool:
        return self.myStage == DriveCharacterization.Stage.kComplete
