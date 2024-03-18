import os
from pathlib import Path

import wpilib
import wpiutil.log
from urcl import URCL
import hal
import commands2
import ntcore
import RobotContainer
from util.LoggedPDP import *
from util.LoggedConsole import *
from util.LoggedSystemStats import *

class MyRobot(wpilib.TimedRobot):
    def robotInit(self):
        # Start Logging using the built in DataLogManager
        logDir = '/U/logs' if wpilib.RobotBase.isReal() else '.logs'
        wpilib.DataLogManager.start( dir=(logDir if Path(logDir).is_dir() else ''), period=1.0 )
        wpilib.DriverStation.startDataLog( wpilib.DataLogManager.getLog() )

        self.m_robotContainer = RobotContainer.RobotContainer()
        hal.report(
            hal.tResourceType.kResourceType_Framework,
            hal.tInstances.kFramework_Timed
        )

        # Disable Watchdog Warning
        wpilib.Watchdog( 0.05, lambda: None ).suppressTimeoutMessage(True)

        # Rev Raw Logging
        URCL.start()

        # Setup Console Logging
        loggedConsole:LoggedConsole = None
        if wpilib.RobotBase.isReal():
            loggedConsole = LoggedConsoleRIO()
        else:
            loggedConsole = LoggedConsoleSIM()
        self.addPeriodic( loggedConsole.periodic, 0.25, 0.016 )

        # Setup PDP Logging
        loggedPDP:LoggedPDP = LoggedPDP( PowerDistribution.ModuleType.kRev )
        self.addPeriodic( loggedPDP.periodic, 0.10, 0.017 )

        # Setup System Logging
        loggedSystemStats:LoggedSystemStats = LoggedSystemStats()
        self.addPeriodic( loggedSystemStats.periodic, 0.10, 0.018 )

    def robotPeriodic(self):
        commands2.CommandScheduler.getInstance().run()

    def autonomousInit(self):
        self.m_robotContainer.runCalibration()
        self.m_autonomousCommand:commands2.Command = self.m_robotContainer.getAutonomousCommand()

        if self.m_autonomousCommand != None:
            self.m_autonomousCommand.schedule()

    def autonomousPeriodic(self): pass
    def autonomousExit(self):
        if self.m_autonomousCommand != None:
            self.m_autonomousCommand.cancel()

    def teleopInit(self):
        self.m_robotContainer.runCalibration()
        
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
