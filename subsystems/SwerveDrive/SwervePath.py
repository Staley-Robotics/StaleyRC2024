import os
import typing
from pathlib import Path

from wpilib import DriverStation, RobotBase, SendableChooser, getOperatingDirectory
import commands2
from pathplannerlib_custom.auto import AutoBuilder, NamedCommands
from pathplannerlib_custom.config import HolonomicPathFollowerConfig, ReplanningConfig, PIDConstants
from pathplannerlib_custom.controller import PPHolonomicDriveController
from pathplannerlib_custom.path import PathPlannerPath

from subsystems import SwerveDrive, LaunchCalc, Indexer

class SwervePath:
    def __init__(self, drivetrain:SwerveDrive, launchCalc:LaunchCalc, indexer:Indexer):
        self.drivetrain = drivetrain
        self.launchCalc = launchCalc
        self.indexer = indexer
      
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
        if self.indexer.hasNote():
            return self.launchCalc.getRotateAngle()
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

    def getFlyCommand(self) -> commands2.Command:
        return FlyCommand( self.drivetrain, self.indexer )
    
class FlyCommand(commands2.SelectCommand):
    def __init__(self, drivetrain:SwerveDrive, indexer:Indexer):
        self.drivetrain = drivetrain
        self.indexer = indexer

        # Paths
        ampPickup = PathPlannerPath.fromPathFile( "Fly-AmpPickup" )
        ampLaunch = PathPlannerPath.fromPathFile( "Fly-AmpLaunch" )
        sourcePickup = PathPlannerPath.fromPathFile( "Fly-SourcePickup" )
        sourceLaunch = PathPlannerPath.fromPathFile( "Fly-SourceLaunch" )

        super().__init__(
            commands={
                "AmpPickup": AutoBuilder.followPath( ampPickup ).withName("AmpSidePickup"),
                "AmpLaunch": AutoBuilder.followPath( ampLaunch ).withName("AmpSideLaunch"),
                "SourcePickup": AutoBuilder.followPath( sourcePickup ).withName("SourceSidePickup"),
                "SourceLaunch": AutoBuilder.followPath( sourceLaunch ).withName("SourceSideLaunch"),
                "NoFly": commands2.cmd.none()
            },
            selector=self.determineFlyPath
        )

    def initialize(self):
        super().initialize()
        self.setName( f"Fly-{self._selectedCommand.getName()}" )

    def determineFlyPath(self):
        isBlue = DriverStation.getAlliance() == DriverStation.Alliance.kBlue
        isRed = DriverStation.getAlliance() == DriverStation.Alliance.kRed
        isLeft = self.drivetrain.getPose().Y() > 4.14
        isRight = not isLeft
        isAmp = (isBlue and isLeft) or (isRed and isRight)

        if isBlue or isRed:
            side = "Amp" if isAmp else "Source"
            state = "Launch" if self.indexer.hasNote() else "Pickup"
            return f"{side}{state}"
        else:
            return "NoFly"
