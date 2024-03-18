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
from subsystems import SwerveDrive
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
        self.deadband = NTTunableFloat( "/Config/Driver1/Deadband", 0.04, persistent=True )

        self.velocLinear = NTTunableFloat( "/Config/Driver1/VelocityLinear", 3.7, persistent=True )
        self.velocAngular = NTTunableFloat( "/Config/Driver1/VelocityAngular", 2 * math.pi, persistent=True )
        self.halfSpeedLinear = NTTunableFloat( "/Config/Driver1/HalfSpeedLinear", 0.5, persistent=True )
        self.halfSpeedAngular = NTTunableFloat( "/Config/Driver1/HalfSpeedAngular", 0.5, persistent=True )

        self.srlV = NTTunableFloat( "/Config/Driver1/SrlVelocity", 3.0, self.updateSlewRateLimiterVelocity )
        self.srlH = NTTunableFloat( "/Config/Driver1/SrlHolonomic", 3.0, self.updateSlewRateLimiterHolonomic )
        self.srlR = NTTunableFloat( "/Config/Driver1/SrlRotation", 3.0, self.updateSlewRateLimiterRotation )

        self.isFieldRelative = NTTunableBoolean( "/Driver1/isFieldRelative", True, persistent=False )
        self.isHalfSpeed = NTTunableBoolean( "/Driver1/isHalfSpeed", False, persistent=False )
        self.isSqrInputs = NTTunableBoolean( "/Driver1/isSquaredInputs", True, persistent=True )       
        self.isSrl = NTTunableBoolean( "/Driver1/isSlewRateLimited", True, persistent=True )        
        
        self.isAimingSpeaker = NTTunableBoolean( "/Driver1/isAimingSpeaker", False, persistent=False )
        self.isAimingAmp = NTTunableBoolean( "/Driver1/isAimingAmp", False, persistent=False )
        self.isAimingStage = NTTunableBoolean( "/Driver1/isAimingStage", False, persistent=False )

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
        # Holonomic PID
        self.tPid = self.drive.getHolonomicDriveController().getThetaController()

        # Verify Max Speeds
        linear, angular = self.drive.getVelocityConfig()
        velocLinear = min( max( self.velocLinear.get(), 0.0 ), linear )
        velocAngular = min( max( self.velocAngular.get(), 0.0 ), angular )
        if self.velocLinear.get() != velocLinear:
            self.velocLinear.set( velocLinear )
        if self.velocAngular.get() != velocAngular:
            self.velocAngular.set( velocAngular )
        
        # Verify Half Speeds
        halfLinear = min( max( self.halfSpeedLinear.get(), 0.0 ), 1.0 )
        halfAngular = min( max( self.halfSpeedAngular.get(), 0.0 ), 1.0)
        if self.halfSpeedLinear.get() != halfLinear:
            self.halfSpeedLinear.set( halfLinear )
        if self.halfSpeedAngular.get() != halfAngular:
            self.halfSpeedAngular.set( halfAngular )

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

        # Apply Clamped Values
        x = min( max( x, -1.0), 1.0 )
        y = min( max( y, -1.0 ), 1.0 )
        #hX = min( max( hX, -1.0 ), 1.0 )
        #hY = min( max( hY, -1.0 ), 1.0 )
        r = min( max( r, -1.0 ), 1.0 )

        # Square the Inputs
        if self.isSqrInputs.get():
            x *= abs( x )
            y *= abs( y )
            #hX *= abs( hX )
            #hY *= abs( hY )
            r *= abs( r )

        # Slew Rate Limiter
        if self.isSrl.get():
            x = self.srl_vX.calculate( x )
            y = self.srl_vY.calculate( y )
            hX = self.srl_hX.calculate( hX )
            hY = self.srl_hY.calculate( hY )
            r = self.srl_rO.calculate( r )

        # Calculate Half Speed Controls
        magH = 1.0
        if self.isHalfSpeed.get():
            x *= self.halfSpeedLinear.get()
            y *= self.halfSpeedLinear.get()
            r *= self.halfSpeedAngular.get()
            magH = self.halfSpeedAngular.get()
        
        # Calculate / Redetermine veloc_r (Rotation via Holonomic or Buttons)
        if abs(hX) > 0.1 or abs(hY) > 0.1:
            mag = min( max( math.sqrt( hX*hX + hY*hY ), 0), 1 )
            mag = mag * magH
            robotAngle:float = self.drive.getRobotAngle().radians()
            goalAngle:float = Rotation2d( x=hX, y=hY ).radians()
            target = self.tPid.calculate(robotAngle, goalAngle)
            r = target * mag
            r = min( max( r, -1.0), 1.0 )
        else:
            self.tPid.reset( self.drive.getRobotAngle().radians(), self.drive.getRotationVelocity() )
        
        # Determine Velocities
        veloc_x = x * self.velocLinear.get()
        veloc_y = y * self.velocLinear.get()
        veloc_r = r * self.velocAngular.get()

        # Determine when ChassisSpeeds capability to use
        if self.isFieldRelative.get():
            speeds = ChassisSpeeds.fromFieldRelativeSpeeds(
                vx = veloc_x,
                vy = veloc_y,
                omega = veloc_r, # radians per second
                robotAngle = self.drive.getRobotAngle()
            )
        else:
            speeds = ChassisSpeeds(
                vx = veloc_x,
                vy = veloc_y,
                omega = veloc_r
            )

        # Send ChassisSpeeds
        self.drive.runChassisSpeeds(speeds)


    def end(self, interrupted:bool) -> None: pass
    def isFinished(self) -> bool: return False
    def runsWhenDisabled(self) -> bool: return False