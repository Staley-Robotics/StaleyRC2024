import commands2
import commands2.button
import commands2.cmd
import wpilib

import subsystems
import commands
import sequences
import autonomous
import util

class RobotContainer:
    """
    Constructs a RobotContainer for the {Game}
    """
    drivetrain:subsystems.SwerveDrive = None
    phoenix6:bool = False
    testing:bool = False

    def __init__(self):
        """
        
        """
        # Create Subsystems
        self.subsystem = subsystems.SampleSubsystem()
        
        if wpilib.RobotBase.isSimulation() and not self.testing:
            self.drivetrain = subsystems.SwerveDrive(
                [
                    subsystems.SwerveModuleSim("FL",  0.25,  0.25 ), 
                    subsystems.SwerveModuleSim("FR",  0.25, -0.25 ), 
                    subsystems.SwerveModuleSim("BL", -0.25,  0.25 ),
                    subsystems.SwerveModuleSim("BR", -0.25, -0.25 ) 
                ],
                subsystems.GyroPigeon2( 10, "rio", 0 )
            )
        elif self.phoenix6:
            self.drivetrain = subsystems.SwerveDrive(
                [
                    subsystems.SwerveModuleNeoPhx6("FL", 7, 8, 18,  0.25,  0.25,  96.837 ), #211.289)
                    subsystems.SwerveModuleNeoPhx6("FR", 1, 2, 12,  0.25, -0.25,   6.240 ), #125.068) #  35.684)
                    subsystems.SwerveModuleNeoPhx6("BL", 5, 6, 16, -0.25,  0.25, 299.954 ), #223.945)
                    subsystems.SwerveModuleNeoPhx6("BR", 3, 4, 14, -0.25, -0.25,  60.293 )  #65.654)
                ],
                subsystems.GyroPigeon2Phx6( 10, "rio", 0 )
            )
        else:
            self.drivetrain = subsystems.SwerveDrive(
                [
                    subsystems.SwerveModuleNeo("FL", 7, 8, 18,  0.25,  0.25,  96.837 ), #211.289)
                    subsystems.SwerveModuleNeo("FR", 1, 2, 12,  0.25, -0.25,   6.240 ), #125.068) #  35.684)
                    subsystems.SwerveModuleNeo("BL", 5, 6, 16, -0.25,  0.25, 299.954 ), #223.945)
                    subsystems.SwerveModuleNeo("BR", 3, 4, 14, -0.25, -0.25,  60.293 )  #65.654)
                ],
                subsystems.GyroPigeon2( 10, "rio", 0 )
            )

        # Add Subsystems to SmartDashboard
        wpilib.SmartDashboard.putData( "SubsystemName", self.subsystem )

        # Add Commands to SmartDashboard
        wpilib.SmartDashboard.putData( "Command", commands.SampleCommand1() )

        # Configure and Add Autonomous Mode to SmartDashboard
        self.m_chooser = wpilib.SendableChooser()
        self.m_chooser.setDefaultOption("1 - None", commands2.cmd.none() )
        self.m_chooser.addOption("2 - Autonomous Command", autonomous.SampleAuto1() )
        wpilib.SmartDashboard.putData("Autonomous Mode", self.m_chooser)
        
        # Configure Driver 1 Button Mappings
        self.m_driver1 = commands2.button.CommandXboxController(0)
        #self.m_driver1.a().whileTrue( commands.SampleCommand1() )

        # Configure Driver 2 Button Mappings
        self.m_driver1 = commands2.button.CommandXboxController(0)
        #self.m_driver1.a().whileTrue( sequences.SampleSequence() )

        # Configure Default Commands
        #self.subsystem.setDefaultCommand(
        #    commands.SampleCommand1()
        #)
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

    def getAutonomousCommand(self) -> commands2.Command:
        """
        :returns: the autonomous command that has been selected from the ShuffleBoard
        """
        return self.m_chooser.getSelected()
    