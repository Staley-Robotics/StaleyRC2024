import typing

import commands2
import commands2.button
import commands2.cmd
import wpilib
import wpilib.shuffleboard
from wpilib.interfaces import GenericHID

from subsystems import *
from commands import *
from sequences import *
from util import *

#NOTE: swerve sections commented out for other prototyping
class RobotContainer:
    """
    Constructs a RobotContainer for the {Game}
    """
    testing:bool = False
    #controllerConfig:str = "Regional"
    controllerConfig:str = "State"
    #controllerConfig:str = "Practice"

    def __init__(self):
        """
        Initialization
        """
        ### Tunable Variables
        self.driveAutoRotate = NTTunableBoolean( "/Config/Game/AutoRotate", True, persistent=True )
        self.endgameTimer1 = NTTunableFloat( "/Config/Game/EndGameNotifications/1", 30.0, persistent=True )
        self.endgameTimer2 = NTTunableFloat( "/Config/Game/EndGameNotifications/2", 15.0, persistent=True )
       
        self.notifier = NTTunableBoolean( "/Logging/Game/EndGameNotifications", False )
        
        # Create Subsystems
        # IO Systems
        ssModulesIO = None
        ssGyroIO = None
        ssCamerasIO = None
        ssIndexerIO = None
        ssIntakeIO = None
        ssLauncherIO = None
        ssPivotIO = None
        ssLedIO = Led2IOPwm( 9 )
        ssClimberIOLeft = None
        ssClimberIORight = None
        ppCommands = {}

        # Create IO Systems
        if wpilib.RobotBase.isSimulation() and not self.testing:
            ssModulesIO = [
                SwerveModuleIOSim("FL",  0.25,  0.25 ), 
                SwerveModuleIOSim("FR",  0.25, -0.25 ), 
                SwerveModuleIOSim("BL", -0.25,  0.25 ),
                SwerveModuleIOSim("BR", -0.25, -0.25 ) 
            ]
            ssGyroIO = GyroIOPigeon2( 9 )
            ssIntakeIO = IntakeIO()
            ssIndexerIO = IndexerIO()
            ssLauncherIO = LauncherIOSim()
            ssPivotIO = PivotIOSim()
            ssClimberIOLeft = ClimberIO()
            ssClimberIORight = ClimberIO()
        else:
            if wpilib.RobotBase.isSimulation():
                ssModulesIO = [
                    SwerveModuleIOSim("FL",  0.25,  0.25 ), 
                    SwerveModuleIOSim("FR",  0.25, -0.25 ), 
                    SwerveModuleIOSim("BL", -0.25,  0.25 ),
                    SwerveModuleIOSim("BR", -0.25, -0.25 ) 
                ]
            else:
                ssModulesIO = [
                    SwerveModuleIONeo("FL", 7, 8, 18,  0.2667,  0.2667,  97.471 ), #211.289)
                    SwerveModuleIONeo("FR", 1, 2, 12,  0.2667, -0.2667,  5.361 ), #125.068) #  35.684)
                    SwerveModuleIONeo("BL", 5, 6, 16, -0.2667,  0.2667,  298.828 ), #223.945)
                    SwerveModuleIONeo("BR", 3, 4, 14, -0.2667, -0.2667,  60.557 )  #65.654)
                ]
            ssGyroIO = GyroIOPigeon2( 9 )
            ssIntakeIO = IntakeIOFalcon( 20, 21, 0, 5 )
            ssIndexerIO = IndexerIONeo( 22, 2, 1 )
            ssLauncherIO = LauncherIOFalcon( 23, 24 , 3 )
            ssPivotIO = PivotIOFalcon( 25, 26, -76.993 )
            ssClimberIOLeft = ClimberIOTalon( 27, 9, 8 )
            ssClimberIORight = ClimberIOTalon( 28, 7, 6 )

        # Vision
        ssCamerasIO:typing.Tuple[VisionCamera] = [
            VisionCameraLimelight3( "limelight-one" ),
            VisionCameraLimelight3( "limelight-two" ),
            VisionCameraLimelight3( "limelight-three" ),
            VisionCameraLimelight3( "limelight-four" )
        ]

        # Link IO Systems to Subsystems
        self.drivetrain:SwerveDrive = SwerveDrive( ssModulesIO, ssGyroIO )
        self.vision = Vision( ssCamerasIO, self.drivetrain.getOdometry )
        self.intake:Intake = Intake( ssIntakeIO )
        self.feeder:Indexer = Indexer( ssIndexerIO )
        self.pivot:Pivot = Pivot( ssPivotIO )
        self.launcher:Launcher = Launcher( ssLauncherIO )
        self.climber = Climber( ssClimberIOLeft, ssClimberIORight )
        self.launchCalc = LaunchCalc( self.drivetrain.getPose )
        self.led = Led2( ssLedIO )

        ### Triggers (Autonomous Helpers)
        self.autonomousLaunchTrigger = NTTunableBoolean( "/Logging/Game/AutonomousLaunch", False )
        commands2.button.Trigger( RobotState.isAutonomous ).and_( self.autonomousLaunchTrigger.get ).onTrue( IndexerLaunch( self.feeder, lambda: self.launcher.atSpeed() and self.pivot.atSetpoint() ) )
        commands2.button.Trigger( RobotState.isAutonomous ).and_( self.launcher.hasLaunched ).onTrue( commands2.cmd.runOnce( lambda: self.autonomousLaunchTrigger.set(False) ) )
        commands2.button.Trigger( lambda: not RobotState.isAutonomous() ).and_( self.autonomousLaunchTrigger.get ).onTrue( commands2.cmd.runOnce( lambda: self.autonomousLaunchTrigger.set(False) ) )

        # Register Pathplanner Commands
        if wpilib.RobotBase.isSimulation():
            ppCommands = {
                "AutoAmp": commands2.cmd.waitSeconds( 0.50 ), 
                "AutoPivot": commands2.cmd.waitSeconds( 0.50 ),
                "AutoLaunch": commands2.cmd.waitSeconds( 0.50 ).andThen(commands2.cmd.runOnce( lambda: self.feeder.setHasNote(False) )),
                "AutoPickup": commands2.cmd.waitSeconds( 0.50 ).andThen(commands2.cmd.runOnce( lambda: self.feeder.setHasNote(True) )),
                "AutoToss": commands2.cmd.waitSeconds( 0.50 )
            }
        else:
            ppCommands = {
                # "AutoAmp": NoteLaunchAmp(self.feeder, self.launcher, self.pivot),
                # "AutoPivot": PivotAim(self.pivot, self.launchCalc.getLaunchAngle),
                # "AutoLaunch": NoteLaunchSpeakerAuto(self.feeder, self.launcher, self.pivot, self.launchCalc),
                # "AutoPickup": NoteLoadGround(self.intake, self.feeder, self.pivot),
                # "AutoToss": NoteToss( self.feeder, self.launcher, self.pivot )
                "AutoAmp": commands2.cmd.none(),
                "AutoPivot": commands2.cmd.none(),
                "AutoLaunch": commands2.cmd.runOnce(
                        lambda: self.autonomousLaunchTrigger.set(True)
                    ).andThen(
                        commands2.cmd.waitSeconds( 0.05 )
                    ).andThen( commands2.cmd.waitUntil(
                        lambda: not self.autonomousLaunchTrigger.get()
                    ) ),
                "AutoPickup": commands2.cmd.none(),
                "AutoToss": commands2.cmd.none()
            }
        self.pathPlanner = SwervePath( self.drivetrain, self.launchCalc.getRotateAngle, self.feeder.hasNote )   
        self.pathPlanner.setNamedCommands( ppCommands )

        # Add Subsystems to SmartDashboard
        wpilib.SmartDashboard.putData( "SwerveDrive", self.drivetrain )
        wpilib.SmartDashboard.putData( "Intake", self.intake )
        wpilib.SmartDashboard.putData( "Indexer", self.feeder )
        wpilib.SmartDashboard.putData( "Pivot", self.pivot )
        wpilib.SmartDashboard.putData( "Launcher", self.launcher )
        wpilib.SmartDashboard.putData( "Climber", self.climber )
        wpilib.SmartDashboard.putData( "LED", self.led )

        # Add Commands to SmartDashboard
        #wpilib.SmartDashboard.putData( "Zero Odometry", commands2.cmd.runOnce( self.drivetrain.resetOdometry ).ignoringDisable(True) )
        wpilib.SmartDashboard.putData( "Set Gyro Offset", commands2.cmd.runOnce( lambda: self.drivetrain.syncGyro() ).ignoringDisable(True) )
        wpilib.SmartDashboard.putData( "LauncherSpeaker", LauncherSpeaker(self.launcher) )
        wpilib.SmartDashboard.putData( "LedButton", LedAction(self.led))

        # Configure and Add Autonomous Mode to SmartDashboard
        self.m_chooser = wpilib.SendableChooser()
        self.m_chooser.setDefaultOption("1 - None", commands2.cmd.none() )
        self.pathPlanner.updatePathPlannerAutoList( self.m_chooser )
        wpilib.SmartDashboard.putData("Autonomous Mode", self.m_chooser)

        # Configure Driver 1 Button Mappings
        self.driver = commands2.button.CommandXboxController(0)
        self.operator = commands2.button.CommandXboxController(1)
        self.station = CrescendoConsole(2)

        # Operator Switches
        if RobotBase.isSimulation():
            self.swIntakeAuto:bool = False
            self.swLaunchStartAuto:bool = False
            self.swLaunchScoreAuto:bool = False
            self.swPivotAuto:bool = False
            self.swPivotManual:bool = False
            self.swClimb:bool = False

            def getSwitchIntakeAuto() -> bool: return self.swIntakeAuto
            def getSwitchPivotAuto() -> bool: return self.swPivotAuto
            def getSwitchPivotManual() -> bool: return self.swPivotManual 
            def getSwitchLaunchStartAuto() -> bool: return self.swLaunchStartAuto
            def getSwitchLaunchScoreAuto() -> bool: return self.swLaunchScoreAuto
            def getSwitchClimb() -> bool: return self.swClimb

            def updateNtLogging():
                ntTbl = NetworkTableInstance.getDefault().getTable("/Logging/Switches")
                ntTbl.putBoolean( "IntakeAuto", getSwitchIntakeAuto() )
                ntTbl.putBoolean( "PivotAuto", getSwitchPivotAuto() )
                ntTbl.putBoolean( "PivotManual", getSwitchPivotManual() )
                ntTbl.putBoolean( "LaunchStartAuto", getSwitchLaunchStartAuto() )
                ntTbl.putBoolean( "LaunchScoreuto", getSwitchLaunchScoreAuto() )
                #ntTbl.putBoolean( "Climb", getSwitchClimb() )
            
            def toggleSwitchIntakeAuto(): self.swIntakeAuto = not self.swIntakeAuto; updateNtLogging()
            def toggleSwitchLaunchStartAuto(): self.swLaunchStartAuto = not self.swLaunchStartAuto; updateNtLogging()
            def toggleSwitchLaunchScoreAuto(): self.swLaunchScoreAuto = not self.swLaunchScoreAuto; updateNtLogging()
            def toggleSwitchPivotAuto(): self.swPivotAuto = not self.swPivotAuto; updateNtLogging()
            def toggleSwitchPivotManual(): self.swPivotManual = not self.swPivotManual; updateNtLogging()
            def toggleSwitchClimb(): self.swClimb = not self.swClimb; updateNtLogging()

            updateNtLogging()
            #self.station.button(5).onTrue( commands2.cmd.runOnce( toggleSwitchIntakeAuto ).ignoringDisable(True) )
            self.station.buttonToggleLeft().onTrue( commands2.cmd.runOnce( toggleSwitchIntakeAuto ).ignoringDisable(True) )
            self.station.buttonToggleRightBottom().onTrue( commands2.cmd.runOnce( toggleSwitchLaunchScoreAuto ).ignoringDisable(True) )
            self.station.buttonToggleRightTop().onTrue( commands2.cmd.runOnce( toggleSwitchLaunchStartAuto ).ignoringDisable(True) )
            self.station.buttonToggleMiddleTop().onTrue( commands2.cmd.runOnce( toggleSwitchPivotAuto ).ignoringDisable(True) )
            self.station.buttonToggleMiddleBottom().onTrue( commands2.cmd.runOnce( toggleSwitchPivotManual ).ignoringDisable(True) )
            #self.station.button(9).onTrue( commands2.cmd.runOnce( toggleSwitchClimb ).ignoringDisable(True) )
        else:
            def getSwitchIntakeAuto() -> bool: return self.station.toggleLeft()
            def toggleSwitchLaunchScoreAuto() -> bool: return self.station.toggleRightBottom()
            def getSwitchLaunchStartAuto() -> bool: return self.station.toggleRightTop()
            def getSwitchPivotAuto() -> bool: return self.station.toggleMiddleTop()
            def getSwitchPivotManual() -> bool: return self.station.toggleMiddleBottom()


        ### Triggers
        triggerTeleop = commands2.button.Trigger( RobotState.isEnabled ).and_( RobotState.isTeleop )
        triggerTargetSpeaker = commands2.button.Trigger( self.launchCalc.isTargetSpeaker )
        triggerHasNote = commands2.button.Trigger( self.feeder.hasNote )
        triggerDriveByStick = commands2.button.Trigger( lambda: self.drivetrain.getCurrentCommand() != None ).and_( lambda: self.drivetrain.getCurrentCommand().getName() == "DriveByStick" )

        triggerTargetAmp = commands2.button.Trigger( self.launchCalc.isTargetAmp )
        triggerTargetTrap = commands2.button.Trigger( self.launchCalc.isTargetTrap )
        triggerTargetToss = commands2.button.Trigger( lambda: False )
        triggerTrapOrNote = triggerTargetTrap.or_( triggerHasNote.getAsBoolean )

        triggerLaunchRotation = commands2.button.Trigger( self.launchCalc.inRotationRange )
        triggerLaunchAngle = commands2.button.Trigger( self.pivot.atSetpoint )
        triggerLaunchRange = triggerLaunchRotation.and_( triggerLaunchAngle.getAsBoolean )
        triggerLaunchReady = triggerLaunchRange.and_( self.launcher.atSpeed )

        triggerSpeakerReady = triggerHasNote.and_( triggerTargetSpeaker.getAsBoolean ).and_( triggerLaunchRange.getAsBoolean )
        triggerAmpReady = triggerHasNote.and_( triggerTargetAmp.getAsBoolean ).and_( triggerLaunchRange.getAsBoolean )

        triggerIntakeRunning = commands2.button.Trigger( self.intake.isRunning )
        
        triggerLauncherRunning = commands2.button.Trigger( self.launcher.isRunning )
        triggerLauncherSpeaker = commands2.button.Trigger( lambda: self.launcher.getCurrentCommand() != None ).and_( lambda: self.launcher.getCurrentCommand().getName() == "LauncherSpeaker" )
        triggerLauncherAmp = commands2.button.Trigger( lambda: self.launcher.getCurrentCommand() != None ).and_( lambda: self.launcher.getCurrentCommand().getName() == "LauncherAmp" )
        triggerLauncherToss = commands2.button.Trigger( lambda: self.launcher.getCurrentCommand() != None ).and_( lambda: self.launcher.getCurrentCommand().getName() == "LauncherToss" )

        triggerPivotSpeaker = commands2.button.Trigger( lambda: self.launcher.getCurrentCommand() != None ).and_( lambda: self.launcher.getCurrentCommand().getName() == "PivotSpeaker" or self.launcher.getCurrentCommand().getName() == "PivotAim" )
        triggerPivotAmp = commands2.button.Trigger( lambda: self.launcher.getCurrentCommand() != None ).and_( lambda: self.launcher.getCurrentCommand().getName() == "PivotAmp" )
        triggerPivotToss = commands2.button.Trigger( lambda: self.launcher.getCurrentCommand() != None ).and_( lambda: self.launcher.getCurrentCommand().getName() == "PivotToss" )

        ### Controller Configs
        if self.controllerConfig == "Regional":
            # Driver 1
            self.driver.leftBumper().whileTrue( DriveFlyByPath( self.drivetrain, self.feeder.hasNote, self.launchCalc.getTarget, lambda: not getSwitchPivotAuto() ) ) # Drive - FlyByPath
            
            self.driver.a().and_( lambda: self.drivetrain.getCurrentCommand() != None ).and_( lambda: self.drivetrain.getCurrentCommand().getName() == "DriveAimAuto"
                ).toggleOnTrue( commands2.cmd.runOnce( lambda: self.drivetrain.getCurrentCommand().cancel() ) )
            self.driver.a().whileTrue( DriveAim( self.drivetrain, self.driver.getLeftY, self.driver.getLeftX, self.launchCalc.getTarget ) )

            #self.driver.b().toggleOnTrue( commands2.cmd.runOnce( lambda: self.launchCalc.setTarget( LaunchCalc.Targets.AMP if self.launchCalc.getTarget() == LaunchCalc.Targets.SPEAKER else LaunchCalc.Targets.SPEAKER ) ) )
            self.driver.x().and_( lambda: not self.feeder.hasNote() and not self.launcher.isRunning() ).toggleOnTrue( IntakeLoad( self.intake ) )
            self.driver.x().and_( self.feeder.hasNote ).and_( self.launchCalc.isTargetSpeaker
                ).and_( lambda: self.launcher.getCurrentCommand() == None or self.launcher.getCurrentCommand().getName() != "LauncherSpeaker"
                ).toggleOnTrue( LauncherSpeaker( self.launcher, self.launchCalc.getDistance ) )
            self.driver.x().and_( self.feeder.hasNote ).and_( self.launchCalc.isTargetAmp
                ).and_( lambda: self.launcher.getCurrentCommand() == None or self.launcher.getCurrentCommand().getName() != "LauncherAmp"
                ).toggleOnTrue( LauncherAmp( self.launcher ) )  
            self.driver.x().and_( self.feeder.hasNote ).onTrue( IndexerLaunch( self.feeder, self.launcher.atSpeed ) )
            # self.driver.y().onTrue()
            # self.driver.leftBumper().toggleOnTrue( ToggleHalfSpeed() )  # Toggle Half Speed
            self.driver.rightBumper().toggleOnTrue( ToggleTurboOn() )  # Toggle Turbo On
            self.driver.rightBumper().toggleOnFalse( ToggleTurboOff() )  # Toggle Turbo Off
            self.driver.back().onTrue( ToggleFieldRelative() ) # Toggle Field Relative
            self.driver.start().onTrue( LedAction( self.led ) ) # LEDs

            #  Driver 2
            self.operator.a().and_( lambda: self.drivetrain.getCurrentCommand() != None ).and_( lambda: self.drivetrain.getCurrentCommand().getName() == "DriveAimAuto"
                ).toggleOnTrue( commands2.cmd.runOnce( lambda: self.drivetrain.getCurrentCommand().cancel() ) )
            self.operator.a().whileTrue( DriveAim( self.drivetrain, self.driver.getLeftY, self.driver.getLeftX, self.launchCalc.getTarget ) )
            self.operator.back().toggleOnTrue( commands2.cmd.runOnce( lambda: self.launchCalc.setTarget( LaunchCalc.Targets.AMP if self.launchCalc.getTarget() == LaunchCalc.Targets.SPEAKER else LaunchCalc.Targets.SPEAKER ) ) )
            self.operator.x().and_( lambda: not self.feeder.hasNote() and not self.launcher.isRunning() ).toggleOnTrue( IntakeLoad( self.intake ) )
            self.operator.x().and_( self.feeder.hasNote ).and_( self.launchCalc.isTargetSpeaker
                ).and_( lambda: self.launcher.getCurrentCommand() == None or self.launcher.getCurrentCommand().getName() != "LauncherSpeaker"
                ).toggleOnTrue( LauncherSpeaker( self.launcher, self.launchCalc.getDistance ) )
            self.operator.x().and_( self.feeder.hasNote ).and_( self.launchCalc.isTargetAmp
                ).and_( lambda: self.launcher.getCurrentCommand() == None or self.launcher.getCurrentCommand().getName() != "LauncherAmp"
                ).toggleOnTrue( LauncherAmp( self.launcher ) ) 
            self.operator.x().and_( self.feeder.hasNote ).toggleOnTrue( IndexerLaunch( self.feeder, self.launcher.atSpeed ) )
            self.operator.y().toggleOnTrue( PivotBottom( self.pivot ) ) # Pivot Down
            self.operator.rightBumper().whileTrue( AllStop( self.intake, self.feeder, self.launcher, self.pivot ) )
            self.operator.start().onTrue( LedAction( self.led ) )

            self.operator.povUp().onTrue(
                commands2.cmd.runOnce( lambda: self.launchCalc.modifyAimAdjust( 0.5 ) ).ignoringDisable(True)
            )
            self.operator.povDown().onTrue(
                commands2.cmd.runOnce( lambda: self.launchCalc.modifyAimAdjust( -0.5 ) ).ignoringDisable(True)
            )
            
            ### Operator Station Buttons 
            self.station.buttonLeftGreen().toggleOnTrue( IntakeLoad( self.intake ) ) # Intake
            #self.station.buttonLeftBlue().toggleOnTrue( LauncherSource( self.launcher ) ) # Source
            #self.station.buttonLeftBlue().and_( lambda: self.launcher.getCurrentCommand() == None or self.launcher.getCurrentCommand().getName() != "LauncherToss"
            #    ).toggleOnTrue( LauncherToss( self.launcher ) ) # LauncherToss
            #self.station.buttonLeftBlue().and_
            self.station.buttonLeftBlue().toggleOnTrue( IndexerLaunch( self.feeder, self.launcher.atSpeed ) ) # Toss
            self.station.buttonRightBlue().toggleOnTrue( NoteToss( self.feeder, self.launcher, self.pivot ) ) # LauncherToss
            # self.station.buttonRightBlue().and_( lambda: self.launcher.getCurrentCommand() == None or ( self.launcher.getCurrentCommand() != None and self.launcher.getCurrentCommand().getName() != "LauncherAmp" )
            #     ).toggleOnTrue( LauncherToss( self.launcher ) ) # LauncherToss
            # self.station.buttonRightBlue().toggleOnTrue( IndexerLaunch( self.feeder, lambda: ( self.launcher.atSpeed() and self.pivot.atSetpoint() ) ) ) # Toss
            self.station.buttonRightGreen().and_( lambda: self.launcher.getCurrentCommand() == None or ( self.launcher.getCurrentCommand() != None and self.launcher.getCurrentCommand().getName() != "LauncherSpeaker" )
                ).toggleOnTrue( LauncherSpeaker( self.launcher, self.launchCalc.getDistance ) ) # Launch Speaker/Amp
            self.station.buttonRightGreen().toggleOnTrue( IndexerLaunch( self.feeder, self.launcher.atSpeed ) ) # Launch
            # Eject
            self.station.buttonLeftRed().whileTrue( EjectAll( self.intake, self.feeder, self.launcher, self.pivot ) ) #Eject
            self.station.buttonRightYellow().whileTrue( AllStop( self.intake, self.feeder, self.launcher, self.pivot ) ) #ALl Stop
            self.station.buttonMiddleWhite().whileTrue( LedAction( self.led ) )
        elif self.controllerConfig == "State":
            # Driver
            self.driver.a().whileTrue( DriveFlyByPath( self.drivetrain, self.feeder.hasNote, self.launchCalc.getTarget, lambda: not getSwitchPivotAuto() ) )
            DoublePressTrigger.doublePress( self.driver.b() ).onTrue( ToggleTarget( self.launchCalc ) )
            self.driver.x().whileTrue( LedAction( self.led ) )
            DoublePressTrigger.doublePress( self.driver.y() ).onTrue( ToggleClimb( self.launchCalc ) )
            self.driver.leftBumper().whileTrue( EjectAll( self.intake, self.feeder, self.launcher, self.pivot ) )
            self.driver.leftTrigger().and_( triggerHasNote.not_().getAsBoolean ).toggleOnTrue( IntakeLoad( self.intake ) )
            self.driver.rightBumper().whileTrue( ForceFeed( self.intake, self.feeder, self.launcher, self.pivot ) )
            self.driver.rightTrigger().and_( triggerHasNote.getAsBoolean ).and_( triggerLauncherRunning.not_().getAsBoolean
                ).and_( self.launchCalc.isTargetSpeaker ).toggleOnTrue( LauncherSpeaker( self.launcher, self.launchCalc.getDistance ) )
            self.driver.rightTrigger().and_( triggerHasNote.getAsBoolean ).and_( triggerLauncherRunning.not_().getAsBoolean
                ).and_( self.launchCalc.isTargetAmp ).toggleOnTrue( LauncherAmp( self.launcher ) )
            self.driver.rightTrigger().and_( triggerHasNote.getAsBoolean ).onTrue( IndexerLaunch( self.feeder, self.launcher.atSpeed ) )
            #self.driver.leftStick()
            #self.driver.rightStick()
            self.driver.start().onTrue( ToggleFieldRelative() )
            DoublePressTrigger.doublePress( self.driver.back() ).onTrue( commands2.cmd.runOnce( lambda: self.driveAutoRotate.set( not self.driveAutoRotate.get() ) ).ignoringDisable(True) )

            # Operator
            self.operator.a( AllStop( self.intake, self.feeder, self.launcher, self.pivot ) )
            DoublePressTrigger.doublePress( self.operator.b() ).onTrue( ToggleTarget( self.launchCalc ) )
            self.operator.x().whileTrue( LedAction( self.led ) )
            DoublePressTrigger.doublePress( self.operator.y() ).onTrue( ToggleClimb( self.launchCalc ) )
            self.operator.leftBumper().whileTrue( EjectAll( self.intake, self.feeder, self.launcher, self.pivot ) )
            self.operator.leftTrigger().and_( triggerHasNote.not_().getAsBoolean ).toggleOnTrue( IntakeLoad( self.intake ) )
            self.operator.rightBumper().whileTrue( ForceFeed( self.intake, self.feeder, self.launcher, self.pivot ) )
            self.operator.rightTrigger().and_( triggerHasNote.getAsBoolean ).onTrue( IndexerLaunch( self.feeder, triggerLaunchReady.getAsBoolean ) )
            #self.operator.leftStick()
            #self.operator.rightStick()
            #self.operator.start()
            #self.operator.back()
            self.operator.povUp().onTrue(
                commands2.cmd.runOnce( lambda: self.launchCalc.modifyAimAdjust( 0.5 ) ).ignoringDisable(True)
            )
            self.operator.povDown().onTrue(
                commands2.cmd.runOnce( lambda: self.launchCalc.modifyAimAdjust( -0.5 ) ).ignoringDisable(True)
            )
            
            ### Operator Station Buttons 
            self.station.buttonLeftGreen().toggleOnTrue( IntakeLoad( self.intake ) ) # Intake
            self.station.buttonLeftBlue().onTrue( ToggleTarget( self.launchCalc ) ) # Change Targets
            self.station.buttonLeftRed().whileTrue( EjectAll( self.intake, self.feeder, self.launcher, self.pivot ) ) #Eject
            self.station.buttonRightGreen().and_( lambda: self.launcher.getCurrentCommand() == None or ( self.launcher.getCurrentCommand() != None and self.launcher.getCurrentCommand().getName() != "LauncherSpeaker" )
                ).toggleOnTrue( LauncherSpeaker( self.launcher, self.launchCalc.getDistance ) ) # Launch Speaker/Amp
            self.station.buttonRightGreen().toggleOnTrue( IndexerLaunch( self.feeder, self.launcher.atSpeed ) ) # Launch
            self.station.buttonRightBlue().toggleOnTrue( NoteToss( self.feeder, self.launcher, self.pivot ) ) # LauncherToss
            self.station.buttonRightYellow().whileTrue( AllStop( self.intake, self.feeder, self.launcher, self.pivot ) ) #ALl Stop
            self.station.buttonMiddleWhite().whileTrue( LedAction( self.led ) ) # Distraction / Celebration
        elif self.controllerConfig == "Testing":
            pass

        ### Configure Default Commands (with Operatory Station Toggles integrated)
        # Auto Aim while holding note

        # DriveTrain
        if self.controllerConfig == "Regional":
            commands2.button.Trigger( RobotState.isEnabled ).and_( RobotState.isTeleop ).and_( self.feeder.hasNote ).onTrue(
                DriveAim( self.drivetrain, self.driver.getLeftY, self.driver.getLeftX, self.launchCalc.getTarget ).withName( "DriveAimAuto" )
            )
            commands2.button.Trigger( RobotState.isEnabled ).and_( RobotState.isTeleop ).and_( lambda: not self.feeder.hasNote() ).and_(
                lambda: self.drivetrain.getCurrentCommand() != None ).and_( lambda: self.drivetrain.getCurrentCommand().getName() != "DriveByStick"
                ).onTrue( commands2.cmd.runOnce( lambda: self.drivetrain.getCurrentCommand().cancel() )
            )

            self.drivetrain.setDefaultCommand(
                DriveByStick(
                    self.drivetrain,
                    self.driver.getLeftY,
                    self.driver.getLeftX,
                    self.driver.getRightY,
                    self.driver.getRightX,
                    lambda: self.driver.getLeftTriggerAxis() - self.driver.getRightTriggerAxis()
                )
            )
        elif self.controllerConfig == "State":           
            triggerTeleop.and_( triggerTrapOrNote.getAsBoolean ).and_( triggerDriveByStick.getAsBoolean ).and_( self.driveAutoRotate.get ).onTrue(
                DriveToRotation( self.drivetrain, self.driver.getLeftY, self.driver.getLeftX, self.launchCalc.getRotateAngle ).withName( "DriveAimAuto" )
            )
            triggerTeleop.and_( triggerTrapOrNote.not_().getAsBoolean ).and_( triggerDriveByStick.not_().getAsBoolean ).and_( lambda: self.drivetrain.getCurrentCommand() != None ).onTrue(
                commands2.cmd.runOnce( lambda: self.drivetrain.getCurrentCommand().cancel() )
            )

            self.drivetrain.setDefaultCommand(
                DriveByStick(
                    self.drivetrain,
                    self.driver.getLeftY,
                    self.driver.getLeftX,
                    rotate = lambda: -self.driver.getRightX()
                )
            )
        else:
            self.drivetrain.setDefaultCommand(
                DriveByStick(
                    self.drivetrain,
                    self.driver.getLeftY,
                    self.driver.getLeftX,
                    lambda: 0.0, #self.driver.getRightY,
                    lambda: 0.0, #self.driver.getRightX,
                    self.driver.getRightX
                )
            )       

        self.intake.setDefaultCommand(
            IntakeDefault(
                self.intake,
                self.feeder.hasNote,
                pivotAtHandoff = self.pivot.atPositionHandoff,
                useAutoStart = getSwitchIntakeAuto
            )
        )
        self.pivot.setDefaultCommand(
            PivotDefault(
                self.pivot,
                self.feeder.hasNote,
                self.launchCalc.getLaunchAngle,
                getAdjustAxis = lambda: ( self.operator.getLeftY() + self.station.getX() ),
                isTargetAmp = self.launchCalc.isTargetAmp,
                isIntakeQueued = lambda: (self.intake.isRunning() or self.intake.hasNote()),
                useAutoCalculate = getSwitchPivotAuto,
                useManualAdjust = getSwitchPivotManual
            )
        )
        # Cancels Launcher Command for Invalid Auto State
        # triggerPivotAuto = commands2.button.Trigger( getSwitchPivotAuto )
        # triggerPivotBadSpeaker = triggerPivotSpeaker.and_( triggerTargetSpeaker.not_().getAsBoolean )
        # triggerPivotBadAmp = triggerPivotAmp.and_( triggerTargetAmp.not_().getAsBoolean )
        # triggerPivotBadToss = triggerPivotToss.and_( triggerTargetToss.not_().getAsBoolean )
        # triggerPivotInvalid = triggerPivotBadSpeaker.or_( triggerPivotBadAmp.getAsBoolean ).or_( triggerPivotBadToss.getAsBoolean )
        # triggerPivotAuto.and_( triggerPivotInvalid.getAsBoolean ).onTrue( commands2.cmd.runOnce( lambda: self.launcher.getCurrentCommand().cancel() ) )

        self.feeder.setDefaultCommand(
            IndexerDefault(
                self.feeder,
                self.intake.hasNote,
                self.pivot.atPositionHandoff,
                self.launchCalc.isAutoLaunchApproved
            )
        )
        self.launcher.setDefaultCommand(
            LauncherDefault(
                self.launcher,
                self.launchCalc.getDistance,
                isIndexerReady = lambda: ( self.feeder.hasNote() and not self.feeder.isRunning() ),
                isTargetAmp = self.launchCalc.isTargetAmp,
                useAutoStart = getSwitchLaunchStartAuto
            )
        )
        # Cancels Launcher Command for Invalid Auto State
        triggerLauncherAuto = commands2.button.Trigger( getSwitchLaunchStartAuto )
        triggerLauncherBadIntake = triggerLauncherRunning.and_( triggerIntakeRunning.getAsBoolean )
        triggerLauncherBadSpeaker = triggerLauncherSpeaker.and_( triggerTargetSpeaker.not_().getAsBoolean )
        triggerLauncherBadAmp = triggerLauncherAmp.and_( triggerTargetAmp.not_().getAsBoolean )
        triggerLauncherBadToss = triggerLauncherToss.and_( triggerTargetToss.not_().getAsBoolean )
        triggerLauncherInvalid = triggerLauncherBadIntake.or_( triggerLauncherBadSpeaker.getAsBoolean ).or_( triggerLauncherBadAmp.getAsBoolean ).or_( triggerLauncherBadToss.getAsBoolean )
        triggerLauncherAuto.and_( triggerLauncherInvalid.getAsBoolean ).onTrue( commands2.cmd.runOnce( lambda: self.launcher.getCurrentCommand().cancel() ) )

        self.climber.setDefaultCommand(
            ClimberDefault(
                self.climber,
                lambda: -( self.station.getY() + self.operator.getRightY() ),
                lambda: True #getSwitchClimb
            )
        )

        ### LED Configuration
        self.led.setIntakeIsRunning( self.intake.isRunning )
        self.led.setIntakeHasNote( self.intake.hasNote )
        self.led.setIndexerHasNote( self.feeder.hasNote )
        self.led.setPivotAutoAdjust( getSwitchPivotAuto )
        self.led.setPivotAtSetpoint( self.pivot.atSetpoint )
        self.led.setLaunchRotation( self.launchCalc.inRotationRange )
        self.led.setLaunchRangeFar( self.launchCalc.inFarRange )
        self.led.setLaunchRangeNear( self.launchCalc.inNearRange )
        self.led.setLaunchRangeAuto( self.launchCalc.inAutoRange )
        self.led.setIsClimb( self.launchCalc.isTargetTrap )
        self.led.setIsEndgame( self.notifier.get )

        ### End Game Notifications
        self.setEndgameNotification( self.endgameTimer1.get, 1.0, 1, 0.5 ) # First Notice
        self.setEndgameNotification( self.endgameTimer2.get, 0.5, 2, 0.5 ) # Second Notice

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
                        self.driver.getHID().setRumble( GenericHID.RumbleType.kBothRumble, 1.0 ),
                        self.operator.getHID().setRumble( GenericHID.RumbleType.kBothRumble, 1.0 ),
                        self.notifier.set( True ) # Visualization on Dashboard
                    )
                ).withTimeout( rumbleTime )
            )
            # Stop Rumble
            rumbleSequence = rumbleSequence.andThen(
                commands2.cmd.run(
                    lambda: (
                        self.driver.getHID().setRumble( GenericHID.RumbleType.kBothRumble, 0.0 ),
                        self.operator.getHID().setRumble( GenericHID.RumbleType.kBothRumble, 0.0 ),
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
        self.drivetrain.syncGyro()
        

