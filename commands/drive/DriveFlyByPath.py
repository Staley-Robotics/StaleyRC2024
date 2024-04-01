import typing

from commands2 import SelectCommand
import commands2.cmd
from wpilib import DriverStation

from pathplannerlib_custom.auto import AutoBuilder
from pathplannerlib_custom.path import PathPlannerPath
from subsystems import SwerveDrive
from util import LaunchCalc

class DriveFlyByPath(SelectCommand):
    def __init__( self,
                  drivetrain:SwerveDrive,
                  hasNote:typing.Callable[[],bool],
                  getTarget:typing.Callable[[],LaunchCalc.Targets],
                  driveToSpeaker:typing.Callable[[],bool]
                ):
        # Subsystems
        self.drivetrain = drivetrain
        
        # Callables
        self.hasNote = hasNote
        self.getTarget = getTarget
        self.driveToSpeaker = driveToSpeaker

        # Paths
        ampA = PathPlannerPath.fromPathFile( "Fly-ToAmp-A" )
        ampB = PathPlannerPath.fromPathFile( "Fly-ToAmp-B" )
        ampD = PathPlannerPath.fromPathFile( "Fly-ToAmp-D" )
        sourceA = PathPlannerPath.fromPathFile( "Fly-ToSource-A" )
        sourceC = PathPlannerPath.fromPathFile( "Fly-ToSource-C" )
        sourceD = PathPlannerPath.fromPathFile( "Fly-ToSource-D" )
        speakerA = PathPlannerPath.fromPathFile( "Fly-ToSpeaker-A" )
        speakerB = PathPlannerPath.fromPathFile( "Fly-ToSpeaker-B" )
        speakerC = PathPlannerPath.fromPathFile( "Fly-ToSpeaker-C" )
        speakerD = PathPlannerPath.fromPathFile( "Fly-ToSpeaker-D" )
        speakerFixedA = PathPlannerPath.fromPathFile( "Fly-ToSpeakerFixed-A" )
        speakerFixedB = PathPlannerPath.fromPathFile( "Fly-ToSpeakerFixed-B" )

        super().__init__(
            commands={
                "ToAmp-A": AutoBuilder.followPath( ampA ).withName("ToAmp-A"),
                "ToAmp-B": AutoBuilder.followPath( ampB ).withName("ToAmp-B"),
                "ToAmp-D": AutoBuilder.followPath( ampD ).withName("ToAmp-D"),
                "ToSpeaker-A": AutoBuilder.followPath( speakerA ).withName("ToSpeaker-A"),
                "ToSpeaker-B": AutoBuilder.followPath( speakerB ).withName("ToSpeaker-B"),
                "ToSpeaker-C": AutoBuilder.followPath( speakerC ).withName("ToSpeaker-C"),
                "ToSpeaker-D": AutoBuilder.followPath( speakerD ).withName("ToSpeaker-D"),
                "ToSpeakerFixed-A": AutoBuilder.followPath( speakerFixedA ).withName("ToSpeakerFixed-A"),
                "ToSpeakerFixed-B": AutoBuilder.followPath( speakerFixedB ).withName("ToSpeakerFixed-B"),
                "ToSource-A": AutoBuilder.followPath( sourceA ).withName("ToSource-A"),
                "ToSource-C": AutoBuilder.followPath( sourceC ).withName("ToSource-C"),
                "ToSource-D": AutoBuilder.followPath( sourceD ).withName("ToSource-D"),
                "NoFly": commands2.cmd.none()
            },
            selector=self.determineFlyPath
        )
        self.addRequirements( self.drivetrain )

    def initialize(self):
        super().initialize()
        self.setName( f"Fly-{self._selectedCommand.getName()}" )

    def determineFlyPath(self):
        pose = self.drivetrain.getPose()

        isBlue = DriverStation.getAlliance() == DriverStation.Alliance.kBlue
        isRed = DriverStation.getAlliance() == DriverStation.Alliance.kRed
        isFar = pose.X() > ( 10.75 if not self.hasNote() else ( 5.85 if self.getTarget() == LaunchCalc.Targets.AMP else ( 2.00 if self.getTarget() == LaunchCalc.Targets.SPEAKER else 0.0 ) ) )
        isLeft = pose.Y() > ( 4.14 if not ( self.getTarget() == LaunchCalc.Targets.SPEAKER and not isFar ) else ( 5.25 if isBlue else ( 8.31 - 5.25 if isRed else 0.0 ) ) )
        isAmpSide = (isBlue and isLeft) or (isRed and not isLeft)

        # Determine Target and Zone
        if not self.hasNote():
            returnStr = "ToSource"
            
            if isAmpSide:
                if isFar: returnStr += "-A"
                else: returnStr += "-C"
            else: returnStr += "-D"
        elif self.getTarget() == LaunchCalc.Targets.SPEAKER:
            returnStr = "ToSpeaker"
            
            if isFar:
                if self.driveToSpeaker(): returnStr += "Fixed"
                
                if isAmpSide: returnStr += "-A"
                else: returnStr += "-B"
            else:
                if isAmpSide: returnStr += "-C"
                else: returnStr += "-D"
        elif self.getTarget() == LaunchCalc.Targets.AMP:
            returnStr = "ToAmp"
            
            if isAmpSide: returnStr += "-A"
            else:
                if isFar: returnStr += "-B"
                else: returnStr += "-D"
        else:
            returnStr = "NoFly"

        return returnStr
