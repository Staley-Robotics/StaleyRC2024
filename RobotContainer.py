import os
import typing
from pathlib import Path

import commands2
import commands2.button
import commands2.cmd
import wpilib
import wpilib.shuffleboard
import wpimath
from wpilib.interfaces import GenericHID

from pathplannerlib.auto import NamedCommands, AutoBuilder
from pathplannerlib.path import PathPlannerPath

from subsystems import *
from commands import *
from sequences import *
from autonomous import *
from util import *

#NOTE: swerve sections commented out for other prototyping
class RobotContainer:
    """
    Constructs a RobotContainer for the {Game}
    """
    testing:bool = False

    def __init__(self):
        """
        Initialization
        """
        ### Tunable Variables
        self.endgameTimer1 = NTTunableFloat( "/Config/Game/EndGameNotifications/1", 30.0 )
        self.endgameTimer2 = NTTunableFloat( "/Config/Game/EndGameNotifications/2", 15.0 )
        self.notifier = NTTunableBoolean( "/Logging/Game/EndGameNotifications", False )
        self.aimAdjust = NTTunableFloat( "/Config/PivotPositions/AutoAimAdjust", 0.0, persistent=True )

        # Create Subsystems
        # IO Systems
        ssModulesIO = None
        ssGyroIO = None
        ssCamerasIO = None
        ssIndexerIO = None
        ssIntakeIO = None
        ssLauncherIO = None
        ssPivotIO = None
        ssElevatorIO = None
        ssLedIO = None
        ssClimberIOLeft = None
        ssClimberIORight = None

        # Create IO Systems
        if wpilib.RobotBase.isSimulation() and not self.testing:
            ssModulesIO = [
                SwerveModuleIOSim("FL",  0.25,  0.25 ), 
                SwerveModuleIOSim("FR",  0.25, -0.25 ), 
                SwerveModuleIOSim("BL", -0.25,  0.25 ),
                SwerveModuleIOSim("BR", -0.25, -0.25 ) 
            ]
            ssGyroIO = GyroIOPigeon2( 9, 0 )
            ssIntakeIO = IntakeIOSim()
            ssIndexerIO = IndexerIOSim()
            ssLauncherIO = LauncherIOSim()
            ssPivotIO = PivotIOSim()
            ssElevatorIO = ElevatorIO()
            ssLedIO = LedIOSim( 9 )
            ssClimberIOLeft = ClimberIO()
            ssClimberIORight = ClimberIO()
        else:
            ssModulesIO = [
                SwerveModuleIONeo("FL", 7, 8, 18,  0.2667,  0.2667,  97.471 ), #211.289)
                SwerveModuleIONeo("FR", 1, 2, 12,  0.2667, -0.2667,  5.361 ), #125.068) #  35.684)
                SwerveModuleIONeo("BL", 5, 6, 16, -0.2667,  0.2667,  298.828 ), #223.945)
                SwerveModuleIONeo("BR", 3, 4, 14, -0.2667, -0.2667,  60.557 )  #65.654)
            ]
            ssGyroIO = GyroIOPigeon2( 9, 0 )
            ssIntakeIO = IntakeIOFalcon( 20, 21, 0 )
            ssIndexerIO = IndexerIONeo( 22, 2, 1 )
            ssLauncherIO = LauncherIOFalcon( 23, 24 , 3 ) #LauncherIONeo( 23, 24 , 3 )
            ssPivotIO = PivotIOFalcon( 25, 26, -77.520+1.318 )
            ssElevatorIO = ElevatorIO() #ElevatorIONeo( 27, 28 )
            ssLedIO = LedIO() #LedIOActual( 0 )
            ssClimberIOLeft = ClimberIOTalon( 27, 5 )
            ssClimberIORight = ClimberIOTalon( 28, 6, True )

        # Vision
        ssCamerasIO:typing.Tuple[VisionCamera] = [
            VisionCameraLimelight( "limelight-one" ),
            VisionCameraLimelight( "limelight-two" ),
            VisionCameraLimelight( "limelight-three" ),
            VisionCameraLimelight( "limelight-four" )
        ]

        # Link IO Systems to Subsystems
        self.drivetrain:SwerveDrive = SwerveDrive( ssModulesIO, ssGyroIO )
        self.intake:Intake = Intake( ssIntakeIO )
        self.feeder:Indexer = Indexer( ssIndexerIO )
        self.launcher:Launcher = Launcher( ssLauncherIO )
        self.pivot:Pivot = Pivot( ssPivotIO )
        self.elevator:Elevator = Elevator( ssElevatorIO )
        self.vision = Vision( ssCamerasIO, self.drivetrain.getOdometry )
        self.led = LED( ssLedIO )
        self.climber = Climber( ssClimberIOLeft, ssClimberIORight )

        # Register Pathplanner Commands
        NamedCommands.registerCommand("AutoPivot",
                                      PivotAim(self.pivot, self.drivetrain.getPose)) 
        NamedCommands.registerCommand("AutoLaunch",
                                      NoteLaunchSpeakerAuto(self.feeder, self.launcher, self.pivot, self.elevator, self.drivetrain.getPose)) 
        NamedCommands.registerCommand("AutoPickup",
                                      NoteLoadGround(self.intake, self.feeder, self.pivot, self.elevator)) 

        # Add Subsystems to SmartDashboard
        wpilib.SmartDashboard.putData( "SwerveDrive", self.drivetrain )
        wpilib.SmartDashboard.putData( "Intake", self.intake )
        wpilib.SmartDashboard.putData( "Indexer", self.feeder )
        wpilib.SmartDashboard.putData( "Launcher", self.launcher )
        wpilib.SmartDashboard.putData( "Pivot", self.pivot )
        wpilib.SmartDashboard.putData( "Elevator", self.elevator )
        wpilib.SmartDashboard.putData( "LED", self.led )
        wpilib.SmartDashboard.putData( "Climber", self.climber )

        # Add Commands to SmartDashboard
        wpilib.SmartDashboard.putData( "Zero Odometry", commands2.cmd.runOnce( self.drivetrain.resetOdometry ).ignoringDisable(True) )
        wpilib.SmartDashboard.putData( "Sync Gyro to Pose", commands2.cmd.runOnce( self.drivetrain.syncGyro ).ignoringDisable(True) )
        wpilib.SmartDashboard.putData( "Re-Sync Pivot", commands2.cmd.runOnce( self.pivot.syncEncoder ).ignoringDisable(True) )
        wpilib.SmartDashboard.putData( "Climber Reset", commands.ClimberReset( self.climber ) )
        #wpilib.SmartDashboard.putData( "run led rainbow", runLedRainbow(self.led))

        wpilib.SmartDashboard.putData( "LauncherSpeaker", LauncherSpeaker(self.launcher) )
        #wpilib.SmartDashboard.putData( "Pivot Amp", PivotAmp(self.pivot) )
        #wpilib.SmartDashboard.putData( "Pivot Load", PivotHandoff( self.pivot) )
        #wpilib.SmartDashboard.putData( "Pivot Down", PivotBottom(self.pivot) )

        # Configure and Add Autonomous Mode to SmartDashboard
        self.m_chooser = wpilib.SendableChooser()
        self.m_chooser.setDefaultOption("1 - None", commands2.cmd.none() )
        p = Path( "/home/lvuser/py/deploy/pathplanner/autos" )
        if RobotBase.isSimulation():
            p = Path( "deploy/pathplanner/autos" )
        for e1 in os.scandir( p ):
            if not e1.is_dir() and e1.name.endswith(".auto"):
                f = e1.name.removesuffix(".auto")
                print( f"Loading Auto: {f}" )
                self.m_chooser.addOption( f, AutoBuilder.buildAuto( f ) )
        wpilib.SmartDashboard.putData("Autonomous Mode", self.m_chooser)

        # Configure Driver 1 Button Mappings
        self.m_driver1 = commands2.button.CommandXboxController(0)
        self.m_driver2 = commands2.button.CommandXboxController(1)

        ## Driving
        self.m_driver1.a().whileTrue(
            commands.DriveAimSpeaker(
                self.drivetrain,
                self.m_driver1.getLeftY,
                self.m_driver1.getLeftX
            )
        )
        self.m_driver2.a().whileTrue(
            commands.DriveAimSpeaker(
                self.drivetrain,
                self.m_driver1.getLeftY,
                self.m_driver1.getLeftX
            )
        )

        self.m_driver1.b().whileTrue(
            commands.DriveAimAmp(
                self.drivetrain,
                self.m_driver1.getLeftY,
                self.m_driver1.getLeftX
            )
        )
        self.m_driver2.back().whileTrue(
            commands.DriveAimAmp(
                self.drivetrain,
                self.m_driver1.getLeftY,
                self.m_driver1.getLeftX
            )
        )

        ## Controller Configs for testing
        # Note Action
        self.m_driver1.x().onTrue(
            sequences.NoteAction( self.intake, self.feeder, self.launcher, self.pivot, self.elevator, self.drivetrain.getPose )
        )
        self.m_driver1.y().onTrue(
            sequences.NoteLaunchAmp( self.feeder, self.launcher, self.pivot, self.elevator )
        )
        self.m_driver1.back().onTrue(
            commands.ToggleFieldRelative()
        )
        self.m_driver1.leftBumper().whileTrue(
            commands.ClimberExtend( self.climber )
        )
        self.m_driver1.rightBumper().onTrue(
            commands.ToggleHalfSpeed()
        )
        self.m_driver1.start().onTrue(
            commands2.cmd.runOnce( self.drivetrain.syncGyro ).ignoringDisable(True)
        )
        
        #  Driver 2
        self.m_driver2.x().onTrue(
            sequences.NoteAction( self.intake, self.feeder, self.launcher, self.pivot, self.elevator, self.drivetrain.getPose )
        )
        self.m_driver2.leftBumper().onTrue(
            sequences.NoteLaunchAmp( self.feeder, self.launcher, self.pivot, self.elevator )
        )
        self.m_driver2.b().whileTrue(
           sequences.AllRealign( self.intake, self.feeder, self.launcher, self.pivot, self.elevator )
        )
        self.m_driver2.rightBumper().onTrue(
            sequences.AllStop( self.intake, self.feeder, self.launcher, self.pivot, self.elevator )
        )
        self.m_driver2.y().whileTrue(
            commands.PivotBottom( self.pivot )
        )
        self.m_driver2.start().onTrue(
            sequences.EjectAll( self.intake, self.feeder, self.launcher, self.pivot )
        )

        self.m_driver2.povUp().onTrue(
            commands2.cmd.runOnce(
                lambda: self.aimAdjust.set( self.aimAdjust.get() + 0.5 )
            ).ignoringDisable(True)
        )
        self.m_driver2.povDown().onTrue(
            commands2.cmd.runOnce(
                lambda: self.aimAdjust.set( self.aimAdjust.get() - 0.5 )
            ).ignoringDisable(True)
        )
        
        # # Safety and Other Commands
        # cTab = wpilib.shuffleboard.Shuffleboard.getTab("Commands")
        # cTab.add( "AllStop", sequences.AllStop( self.intake, self.feeder, self.launcher, self.pivot, self.elevator ) ).withPosition(0, 0)
        # cTab.add( "IntakeEject", IntakeEject(self.intake) ).withPosition(0, 1)
        # cTab.add( "IndexerEject", IndexerEject(self.feeder) ).withPosition(0, 2)
        # cTab.add( "PivotBottom", PivotBottom(self.pivot) ).withPosition(1, 2)
        # cTab.add( "PivotTop", PivotTop(self.pivot) ).withPosition(1, 1)

        # # Intake to Ready to Launch Commands
        # cTab.add( "IntakeLoad", IntakeLoad(self.intake) ).withPosition(3, 0)
        # cTab.add( "ElevatorHandoff", ElevatorBottom(self.elevator) ).withPosition(4, 0)
        # cTab.add( "PivotHandoff", PivotHandoff(self.pivot) ).withPosition(5, 0)
        # cTab.add( "IndexerHandoff", IndexerHandoff(self.feeder) ).withPosition(6, 0)
        # cTab.add( "IntakeHandoff", IntakeHandoff(self.intake) ).withPosition(7, 0)

        # # Launch to Speaker Commands
        # cTab.add( "ElevatorSpeaker", ElevatorBottom(self.elevator) ).withPosition(3, 1)
        # cTab.add( "PivotSpeaker", PivotToPosition(self.pivot) ).withPosition(4, 1)
        # cTab.add( "LauncherSpeaker", LauncherSpeaker(self.launcher) ).withPosition(5, 1)
        # cTab.add( "IndexerSpeaker", IndexerLaunch(self.feeder) ).withPosition(6, 1)

        # # Launch to Amp Commands
        # cTab.add( "ElevatorAmp", ElevatorAmp(self.elevator) ).withPosition(3, 2)
        # cTab.add( "PivotAmp", PivotAmp(self.pivot) ).withPosition(4, 2)
        # cTab.add( "LauncherAmp", LauncherAmp(self.launcher) ).withPosition(5, 2)
        # cTab.add( "IndexerAmp", IndexerLaunch(self.feeder) ).withPosition(6, 2)
        
        # # Launch to Trap Commands
        # cTab.add( "ElevatorTrap", ElevatorTrap(self.elevator) ).withPosition(3, 3)
        # cTab.add( "PivotTrap", PivotTrap(self.pivot) ).withPosition(4, 3)
        # cTab.add( "LauncherTrap", LauncherTrap(self.launcher) ).withPosition(5, 3)
        # cTab.add( "IndexerTrap", IndexerLaunch(self.feeder) ).withPosition(6, 3)
        
        # # Source to Launch Commands
        # cTab.add( "ElevatorSource", ElevatorSource(self.elevator) ).withPosition(3, 4)
        # cTab.add( "PivotSource", PivotSource(self.pivot) ).withPosition(4, 4)
        # cTab.add( "IndexerSource", IndexerSource(self.feeder) ).withPosition(5, 4)
        # cTab.add( "LauncherSource", LauncherSource(self.launcher) ).withPosition(6, 4)
        
        # End Game Notifications
        self.setEndgameNotification( self.endgameTimer1.get, 1.0, 1, 0.5 ) # First Notice
        self.setEndgameNotification( self.endgameTimer2.get, 0.5, 2, 0.5 ) # Second Notice

        # Configure Default Commands
        self.drivetrain.setDefaultCommand(
            commands.DriveByStick(
                self.drivetrain,
                self.m_driver1.getLeftY,
                self.m_driver1.getLeftX,
                self.m_driver1.getRightY,
                self.m_driver1.getRightX,
                lambda: self.m_driver1.getLeftTriggerAxis() - self.m_driver1.getRightTriggerAxis()
            )
        )

        self.launcher.setDefaultCommand(
            commands2.ConditionalCommand(
                commands.LauncherSpeaker( self.launcher ),
                commands2.cmd.none(),
                lambda: self.feeder.hasNote() and self.drivetrain.getPose().X() < 4.0
            )
        )

        self.pivot.setDefaultCommand(
            sequences.PivotDefault(
                self.pivot,
                self.drivetrain.getPose,
                self.feeder.hasNote
            )
        )
        
        self.feeder.setDefaultCommand(
            commands.IndexerDefault(
                self.feeder
            )
        )

        self.climber.setDefaultCommand(
            commands.ClimberCollapse(
                self.climber
            )
        )
    
    def setEndgameNotification( self,
                                getAlertTime:typing.Callable[[],float],
                                rumbleTime:float = 1.0,
                                pulseCount:int = 1,
                                pulseDelay:float = 0.5 ) -> None:
        """
        Creates a Customizable End Game Notification and adds is to the Command Scheduler
        
        :param getAlertTime: A lambda function that requests the amount of time (in seconds)
        remaining in the match when the notification occurs
        :param rumbleTime: The amount of time (in seconds) the rumble occurs
        :param pulseCount: The number of times (pulses) the notification occurs
        :param pulseDelay: The amount of time (in seconds) to delay between notification pulses
        """
        # Create Rumble Patterns
        rumbleSequence = commands2.cmd.sequence()
        for i in range(pulseCount):
            # Start Rumble
            rumbleSequence = rumbleSequence.andThen(
                commands2.cmd.run(
                    lambda: (
                        self.m_driver1.getHID().setRumble( GenericHID.RumbleType.kBothRumble, 1.0 ),
                        #self.m_driver2.getHID().setRumble( GenericHID.RumbleType.kBothRumble, 1.0 ),
                        self.notifier.set( True ) # Visualization on Dashboard
                    )
                ).withTimeout( rumbleTime )
            )
            # Stop Rumble
            rumbleSequence = rumbleSequence.andThen(
                commands2.cmd.run(
                    lambda: (
                        self.m_driver1.getHID().setRumble( GenericHID.RumbleType.kBothRumble, 0.0 ),
                        #self.m_driver2.getHID().setRumble( GenericHID.RumbleType.kBothRumble, 0.0 ),
                        self.notifier.set( False ) # Visualization on Dashboard
                    )
                ).withTimeout( pulseDelay )
            )

        # Bind Rumble Triggers to 
        commands2.button.Trigger(
            lambda: ( DriverStation.isTeleopEnabled() 
                and DriverStation.getMatchTime() > 0.0 
                and DriverStation.getMatchTime() <= round( getAlertTime(), 2 )
            )
        ).onTrue( rumbleSequence )

    def getAutonomousCommand(self) -> commands2.Command:
        """
        :returns: the autonomous command that has been selected from the ShuffleBoard
        """
        return self.m_chooser.getSelected()

    def runCalibration(self) -> None:
        """
        Adds the calibration commands to the Command Scheduler
        """
        ClimberResetSwitch( self.climber ).schedule()
        self.drivetrain.syncGyro()