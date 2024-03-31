import os
import typing
from pathlib import Path

from wpilib import DriverStation, SendableChooser, getOperatingDirectory
from wpimath.geometry import Rotation2d

from pathplannerlib_custom.auto import AutoBuilder, NamedCommands
from pathplannerlib_custom.config import HolonomicPathFollowerConfig, ReplanningConfig, PIDConstants
from pathplannerlib_custom.controller import PPHolonomicDriveController
from subsystems import SwerveDrive, LaunchCalc, Indexer

class SwervePath:
    def __init__( self,
                  drivetrain:SwerveDrive,
                  launchRotation:typing.Callable[[],Rotation2d] = lambda: Rotation2d(0),
                  hasNote:typing.Callable[[],bool] = lambda: False
                ):
        # Subsystems
        self.drivetrain = drivetrain
        self.launchRotation = launchRotation
        
        # Callable Functions
        self.hasNote = hasNote
      
        if not AutoBuilder.isConfigured():
            AutoBuilder.configureHolonomic(
                self.drivetrain.getPose, # Robot pose supplier
                self.drivetrain.resetOdometry, # Method to reset odometry (will be called if your auto has a starting pose)
                self.drivetrain.getChassisSpeeds, # ChassisSpeeds supplier. MUST BE ROBOT RELATIVE
                self.drivetrain.runChassisSpeeds, # Method that will drive the robot given ROBOT RELATIVE ChassisSpeeds
                HolonomicPathFollowerConfig( # HolonomicPathFollowerConfig, this should likely live in your Constants class
                    PIDConstants(
                        self.drivetrain.pidX_kP.get(),
                        self.drivetrain.pidX_kI.get(),
                        self.drivetrain.pidX_kD.get()
                    ), # Translation PID constants
                    PIDConstants(
                        self.drivetrain.pidT_kP.get(),
                        self.drivetrain.pidT_kI.get(),
                        self.drivetrain.pidT_kD.get()
                    ), # Rotation PID constants
                    self.drivetrain.maxVelocPhysical.get(), # Max module speed, in m/s
                    self.drivetrain.getRadius(), # Drive base radius in meters. Distance from robot center to furthest module.
                    ReplanningConfig() # Default path replanning config. See the API for the options here
                ),
                self.getPathPlannerFlipPath, # Supplier to control path flipping based on alliance color
                self.drivetrain # Reference to this subsystem to set requirements
            )
        else:
            print( "AutoBuilder Already Built!" )

        PPHolonomicDriveController.setRotationTargetOverride( self.getPathPlannerTarget )

    def setNamedCommands(self, commandDict:typing.Dict = {}):
        for key in commandDict:
            NamedCommands.registerCommand( key, commandDict[key] )

    def getPathPlannerFlipPath(self):
        # return False
        return DriverStation.getAlliance() == DriverStation.Alliance.kRed

    def getPathPlannerTarget(self):
        if self.hasNote():
            return self.launchRotation()
        else:
            return None

    def updatePathPlannerAutoList(self, chooser:SendableChooser) -> dict:
        opDir = getOperatingDirectory()
        p = Path( f"{opDir}/deploy/pathplanner/autos" )
        for e1 in os.scandir( p ):
            if not e1.is_dir() and e1.name.endswith(".auto"):
                f = e1.name.removesuffix(".auto")
                print( f"Loading Auto: {f}" )
                chooser.addOption( f, AutoBuilder.buildAuto( f ) )
    
