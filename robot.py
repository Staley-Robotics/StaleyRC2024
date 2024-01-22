import wpilib
import wpiutil.log
import hal
import commands2
import ntcore
import RobotContainer
from util.LoggedPDP import *
from util.LoggedConsole import *

class MyRobot(wpilib.TimedRobot):
    def __init__(self):
        super().__init__()

        # Setup Console Logging
        loggedConsole:LoggedConsole = None
        if wpilib.RobotBase.isReal():
            #loggedConsole = LoggedConsoleRIO()
            pass
        else:
            loggedConsole = LoggedConsoleSIM()
        #self.addPeriodic( loggedConsole.periodic, 0.02, 0.01 )

        # Setup PDP Logging
        loggedPDP:LoggedPDP = LoggedPDP()
        self.addPeriodic( loggedPDP.periodic, 0.02, 0 )
    
    def robotInit(self):
        # Start Logging using the built in DataLogManager
        if wpilib.RobotBase.isReal():
            wpilib.DataLogManager.start( dir='/U/logs', period=1.0 )
        else:
            wpilib.DataLogManager.start( dir='.logs', period=1.0 )
        wpilib.DriverStation.startDataLog( wpilib.DataLogManager.getLog() )

        self.m_robotContainer = RobotContainer.RobotContainer()
        hal.report(
            hal.tResourceType.kResourceType_Framework,
            hal.tInstances.kFramework_Timed
        )

    def robotPeriodic(self):
        wpilib.setCurrentThreadPriority(True, 99)
        commands2.CommandScheduler.getInstance().run()
        wpilib.setCurrentThreadPriority(True, 10)

    def autonomousInit(self):
        self.m_autonomousCommand:commands2.Command = self.m_robotContainer.getAutonomousCommand()

        if self.m_autonomousCommand != None:
            self.m_autonomousCommand.schedule()

    def autonomousPeriodic(self): pass
    def autonomousExit(self):
        if self.m_autonomousCommand != None:
            self.m_autonomousCommand.cancel()

    def teleopInit(self): pass
    def teleopPeriodic(self): pass
    def teleopExit(self): pass

    def testInit(self): pass
    def testPeriodic(self): pass
    def testExit(self): pass

    def disabledInit(self): pass
    def disabledPeriodic(self): pass
    def disabledExit(self): pass

    def _simulationInit(self): pass
    def _simulationPeriodic(self): pass
    def _simluationExit(self): pass
