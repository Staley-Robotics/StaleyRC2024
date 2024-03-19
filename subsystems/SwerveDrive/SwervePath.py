import os
import typing
from pathlib import Path

from wpilib import DriverStation, RobotBase, SendableChooser
import commands2
from pathplannerlib.auto import AutoBuilder, NamedCommands
from pathplannerlib.config import HolonomicPathFollowerConfig, ReplanningConfig, PIDConstants
from pathplannerlib.controller import PPHolonomicDriveController
from pathplannerlib.path import PathPlannerPath

from subsystems import SwerveDrive, LaunchCalc, Indexer

class SwervePath:
    def __init__(self, drivetrain:SwerveDrive, launchCalc:LaunchCalc, indexer:Indexer):
        self.drivetrain = drivetrain
        self.launchCalc = launchCalc
        self.indexer = indexer
      
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

        PPHolonomicDriveController.setRotationTargetOverride( self.getPathPlannerTarget )

    def setNamedCommands(self, commandDict:typing.Dict = {}):
        for key in commandDict:
            NamedCommands.registerCommand( key, commandDict[key] )

    def getPathPlannerFlipPath(self):
        return DriverStation.getAlliance() == DriverStation.Alliance.kRed

    def getPathPlannerTarget(self):
        if self.indexer.hasNote():
            return self.launchCalc.getRotateAngle()
        elif RobotBase.isSimulation():
            return self.launchCalc.getRotateAngle()
        else:
            return None

    def updatePathPlannerAutoList(self, chooser:SendableChooser) -> dict:
        myPath = Path().resolve()
        pathStr = f"{myPath}"

        # Checking for Appropriate Path based on Sim vs Test vs Real
        if not RobotBase.isSimulation():
            pathStr = "/home/lvuser/py"
        elif myPath.name.endswith("tests"):
            pathStr = f"{pathStr}/.."
        
        p = Path( f"{pathStr}/deploy/pathplanner/autos" )
        for e1 in os.scandir( p ):
            if not e1.is_dir() and e1.name.endswith(".auto"):
                f = e1.name.removesuffix(".auto")
                print( f"Loading Auto: {f}" )
                chooser.addOption( f, AutoBuilder.buildAuto( f ) )

    def getFlyCommand(self) -> commands2.Command:
        def determineFlyPath():
            if DriverStation.getAlliance() == DriverStation.Alliance.kBlue:
                alliance = "Blue"
                side = "Left" if self.drivetrain.getPose().Y() > 4.25 else "Right"
                state = "Launch" if self.indexer.hasNote() else "Pickup"
                return f"{alliance}Fly{side}{state}"
            elif DriverStation.getAlliance() == DriverStation.Alliance.kRed:
                alliance = "Red"
                side = "Right" if self.drivetrain.getPose().Y() > 4.25 else "Left"
                state = "Launch" if True else "Pickup" #self.indexer.hasNote() else "Pickup"
                return f"{alliance}Fly{side}{state}"
            else:
                return f"NoFly"

        # Paths
        blueFlyLeftPickup = PathPlannerPath.fromPathFile( "Fly-BL-Pickup" )
        blueFlyLeftLaunch = PathPlannerPath.fromPathFile( "Fly-BL-Launch" )
        blueFlyRightPickup = PathPlannerPath.fromPathFile( "Fly-BR-Pickup" )
        blueFlyRightLaunch = PathPlannerPath.fromPathFile( "Fly-BR-Launch" )
        redFlyLeftPickup = PathPlannerPath.fromPathFile( "Fly-RL-Pickup" )
        redFlyLeftLaunch = PathPlannerPath.fromPathFile( "Fly-RL-Launch" )
        redFlyRightPickup = PathPlannerPath.fromPathFile( "Fly-RR-Pickup" )
        redFlyRightLaunch = PathPlannerPath.fromPathFile( "Fly-RR-Launch" )
        
        # Build Command
        myCmd = commands2.SelectCommand(
            commands={
                "BlueFlyLeftPickup": AutoBuilder.followPath( blueFlyLeftPickup ),
                "BlueFlyLeftLaunch": AutoBuilder.followPath( blueFlyLeftLaunch ),
                "BlueFlyRightPickup": AutoBuilder.followPath( blueFlyRightPickup ),
                "BlueFlyRightLaunch": AutoBuilder.followPath( blueFlyRightLaunch ),
                "RedFlyLeftPickup": AutoBuilder.followPath( redFlyLeftPickup ),
                "RedFlyLeftLaunch": AutoBuilder.followPath( redFlyLeftLaunch ),
                "RedFlyRightPickup": AutoBuilder.followPath( redFlyRightPickup ),
                "RedFlyRightLaunch": AutoBuilder.followPath( redFlyRightLaunch ),
                "NoFly": commands2.cmd.none()
            },
            selector=determineFlyPath
        )
        myCmd = myCmd.withName( "Fly!" )
        return myCmd