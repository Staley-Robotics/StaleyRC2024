### Imports
# Python Imports
import typing
import math

# FRC Component Imports
from commands2 import Command
from wpimath import applyDeadband
from wpimath.controller import ProfiledPIDControllerRadians
from wpimath.geometry import Rotation2d
from wpimath.filter import SlewRateLimiter
from wpimath.kinematics import ChassisSpeeds
from wpimath.trajectory import TrapezoidProfileRadians

# Our Imports
from subsystems.SwerveDrive import SwerveDrive
from util import *

# Default Drive Command Class
class DriveByStick(Command):
    def __init__( self,
                  swerveDrive:SwerveDrive,
                  velocityX:typing.Callable[[], float],
                  velocityY:typing.Callable[[], float],
                  holonomicX:typing.Callable[[], float] = ( lambda: 0.0 ),
                  holonomicY:typing.Callable[[], float] = ( lambda: 0.0 ), 
                  rotate:typing.Callable[[], float] = ( lambda: 0.0 )
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.setName( "DriveByStick" )
        self.addRequirements( swerveDrive )

        # Tunables
        self.deadband = NTTunableFloat( "/CmdConfig/DriveByStick/Deadband", 0.04 )

        self.finetuneEnabled = NTTunableBoolean( "/CmdConfig/DriveByStick/Control/FineEnabled", False )
        self.ctlFineVelocity = NTTunableFloat( "/CmdConfig/DriveByStick/Control/Fine/Velocity", 0.4 )
        self.ctlFineHolonomic = NTTunableFloat( "/CmdConfig/DriveByStick/Control/Fine/Holonomic", 0.4 )
        self.ctlFineRotation = NTTunableFloat( "/CmdConfig/DriveByStick/Control/Fine/Rotation", 0.4 )

        self.ctlFullVelocity = NTTunableFloat( "/CmdConfig/DriveByStick/Control/Full/Velocity", 0.8 )
        self.ctlFullHolonomic = NTTunableFloat( "/CmdConfig/DriveByStick/Control/Full/Holonomic", 0.8 )
        self.ctlFullRotation = NTTunableFloat( "/CmdConfig/DriveByStick/Control/Full/Rotation", 0.8 )

        self.srlV = NTTunableFloat( "/CmdConfig/DriveByStick/SlewRateLimiter/Velocity", 3.0, self.updateSlewRateLimiterVelocity )
        self.srlH = NTTunableFloat( "/CmdConfig/DriveByStick/SlewRateLimiter/Holonomic", 3.0, self.updateSlewRateLimiterHolonomic )
        self.srlR = NTTunableFloat( "/CmdConfig/DriveByStick/SlewRateLimiter/Rotation", 3.0, self.updateSlewRateLimiterRotation )

        # This Command Global Properties
        self.drive = swerveDrive
        self.vX = velocityX
        self.vY = velocityY
        self.hX = holonomicX
        self.hY = holonomicY
        self.rO = rotate

        # Slew Rate Limiters
        self.updateSlewRateLimiterVelocity()
        self.updateSlewRateLimiterHolonomic()
        self.updateSlewRateLimiterRotation()

    def updateSlewRateLimiterVelocity(self):
        self.srl_vX = SlewRateLimiter( self.srlV.get() )
        self.srl_vY = SlewRateLimiter( self.srlV.get() )

    def updateSlewRateLimiterHolonomic(self):
        self.srl_hX = SlewRateLimiter( self.srlH.get() )
        self.srl_hY = SlewRateLimiter( self.srlH.get() )

    def updateSlewRateLimiterRotation(self):
        self.srl_rO = SlewRateLimiter( self.srlR.get() )

    def initialize(self) -> None:
        self.tPid = self.drive.getHolonomicDriveController().getThetaController()

    def execute(self) -> None:
        # Get Input Values
        x = -self.vX()
        y = -self.vY()
        hX = -self.hX()
        hY = -self.hY()
        r = self.rO()

        # Calculate Deadband
        x = applyDeadband( x, self.deadband.get() ) 
        y = applyDeadband( y, self.deadband.get() )
        hX = applyDeadband( hX, self.deadband.get() )
        hY = applyDeadband( hY, self.deadband.get() )
        r = applyDeadband( r, self.deadband.get() )

        # Square the Inputs
        x *= abs( x )
        y *= abs( y )
        hX *= abs( hX )
        hY *= abs( hY )
        r *= abs( r )

        # Slew Rate Limiter
        #x = self.srl_vX.calculate( x )
        #y = self.srl_vY.calculate( y )
        #hX = self.srl_hX.calculate( hX )
        #hY = self.srl_hY.calculate( hY )
        #r = self.srl_rO.calculate( r )

        # Calculate Fine Tuned Controls
        magV = self.ctlFullVelocity.get() if not self.finetuneEnabled.get() else self.ctlFineVelocity.get()
        magH = self.ctlFullHolonomic.get() if not self.finetuneEnabled.get() else self.ctlFineHolonomic.get()
        magR = self.ctlFullRotation.get() if not self.finetuneEnabled.get() else self.ctlFineRotation.get()           
        x *= magV
        y *= magV
        r *= magR

        # Calculate Rotation via Holonomic or Buttons
        if abs(hX) > 0.1 or abs(hY) > 0.1:
            mag = math.sqrt( hX*hX + hY*hY ) * magH
            robotAngle:float = self.drive.getRobotAngle().radians()
            goalAngle:float = Rotation2d( x=hX, y=hY ).radians()
            target = self.tPid.calculate(robotAngle, goalAngle)
            r = target * mag
            r = min( max( r, -1.0 ), 1.0 )
        elif abs(r) > 0.05:
            self.drive.resetHolonomicDriveController()

        # Send ChassisSpeeds
        self.drive.runPercentageInputs(x, y, r)

    def end(self, interrupted:bool) -> None: pass
    def isFinished(self) -> bool: return False
    def runsWhenDisabled(self) -> bool: return False