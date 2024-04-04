import typing

from commands2 import Subsystem
from wpilib import Color, DriverStation, RobotState, RobotBase, Timer

from .Led2IO import Led2IO
from util import NTTunableBoolean, NTTunableFloat, LaunchCalc

class Led2(Subsystem):
    def __init__(self, led:Led2IO):
        # NT Tunables
        self.offline = NTTunableBoolean( "/DisableSubsystem/Led", False, persistent=True )

        self.strobeDurationFast = NTTunableFloat( "/Config/LedEffects/Strobe/FastDuration", 0.25, persistent=True )
        self.strobeDurationSlow = NTTunableFloat( "/Config/LedEffects/Strobe/SlowDuration", 0.50, persistent=True )
        self.strobeDurationEStop = NTTunableFloat( "/Config/LedEffects/Strobe/EStopDuration", 1.5, persistent=True )
        
        self.breatheDurationFast = NTTunableFloat( "/Config/LedEffects/Breathe/FastDuration", 0.75, persistent=True )
        self.breatheDurationSlow = NTTunableFloat( "/Config/LedEffects/Breathe/SlowDuration", 1.50, persistent=True )
        
        self.rainbowCycleLength = NTTunableFloat( "/Config/LedEffects/Rainbow/CycleLength", 25.0, persistent=True )
        self.rainbowDuration    = NTTunableFloat( "/Config/LedEffects/Rainbow/Duration", 0.25, persistent=True )
        
        self.waveCycleFast        = NTTunableFloat( "/Config/LedEffects/Wave/FastCycleLength", 25.0, persistent=True )
        self.waveDurationFast     = NTTunableFloat( "/Config/LedEffects/Wave/FastDuration", 0.25, persistent=True )
        self.waveCycleSlow        = NTTunableFloat( "/Config/LedEffects/Wave/SlowCycleLength", 25.0, persistent=True )
        self.waveDurationSlow     = NTTunableFloat( "/Config/LedEffects/Wave/SlowDuration", 3.0, persistent=True )
        self.waveCycleAlliance    = NTTunableFloat( "/Config/LedEffects/Wave/AllianceCycleLength", 15.0, persistent=True )
        self.waveDurationAlliance = NTTunableFloat( "/Config/LedEffects/Wave/AllianceDuration", 2.0, persistent=True )
        
        self.stripesDurationFast = NTTunableFloat( "/Config/LedEffects/Stripes/FastDuration", 2.0, persistent=True )
        self.stripesDurationSlow = NTTunableFloat( "/Config/LedEffects/Stripes/SlowDuration", 5.0, persistent=True )

        self.autoFadeTime    = NTTunableFloat( "/Config/LedEffects/AutoFade/Time", 2.5, persistent=True )
        self.autoFadeMaxTime = NTTunableFloat( "/Config/LedEffects/AutoFade/MaxTime", 5.0, persistent=True )

        # Global Variables
        self.led = led

        # Lambda Functions
        self.setIntakeIsRunning()
        self.setIntakeHasNote()
        self.setIndexerHasNote()
        self.setPivotAutoAdjust()
        self.setPivotAtSetpoint()
        self.setLaunchRotation()
        self.setLaunchRangeFar()
        self.setLaunchRangeNear()
        self.setLaunchRangeAuto()
        self.setIsEndgame()
        
        # Color Sets
        self.offColors = Color.kBlack
        self.allianceColor = Color.kBlack
        self.allianceColorDark = Color.kBlack
        self.intakeRunColors = Color.kYellow
        self.hasNoteColors = Color.kOrange
        self.launchFarColors = Color.kGreen
        self.launchNearColors = Color.kPurple
        self.endGameColors = Color.kWhite
        self.staleyColors = [Color.kDarkGreen, Color.kSilver, Color.kGreen, Color.kWhite]
        self.distractionColors = [Color.kWhite, Color.kBlack, Color.kHotPink, Color.kBlack]
        self.invalidColors = Color.kHotPink
        
    def periodic(self):
        # Logger

        # Update Alliance Color
        self.updateAllianceColor()
        
        # Offline State
        if self.offline.get():
            self.led.solid( self.offColors )
        elif self.getCurrentCommand() == None:
            self.runAutomatedState()

        # Run LEDs
        self.led.run()

    def updateAllianceColor(self):
        match DriverStation.getAlliance():
            case DriverStation.Alliance.kBlue:
                self.allianceColor = Color.kBlue
                self.allianceColorDark = Color.kWhiteSmoke
            case DriverStation.Alliance.kRed:
                self.allianceColor = Color.kRed
                self.allianceColorDark = Color.kWhiteSmoke
            case _:
                self.allianceColor = Color.kLightYellow
                self.allianceColorDark = Color.kYellow

    def runAutomatedState(self):
        # Determine State
        if RobotState.isEStopped():
            self.led.strobe( [Color.kDarkRed], self.strobeDurationEStop.get() )
        elif RobotState.isDisabled():
            self.led.wave( self.allianceColor, self.allianceColorDark, self.waveCycleAlliance.get(), self.waveDurationAlliance.get() )
        elif RobotState.isAutonomous():
            self.led.wave( self.allianceColor, self.allianceColorDark, self.waveCycleFast.get(), self.waveDurationFast.get() )
        elif self.isEndgame():
            self.led.strobe( [self.endGameColors], self.strobeDurationFast.get() )
        elif RobotState.isTeleop():
            # Default State, Rate, and Color
            blink = False
            slow = True
            color = self.allianceColor

            # Determine State    
            if self.indexerHasNote():
                if self.launchAimGood():
                    if self.launchRangeFar():
                        blink = True
                    if self.launchRangeNear():
                        slow = False
            elif self.intakeHasNote():
                blink = True
                if not self.intakeIsRunning():
                    slow = False
            elif self.intakeIsRunning():
                blink = True

            # Determine Color
            if self.indexerHasNote():
                if self.launchRangeNear():
                    color = self.launchNearColors
                elif self.launchRangeFar():
                    color = self.launchFarColors
                else:
                    color = self.hasNoteColors
            elif self.intakeIsRunning() or self.intakeHasNote():
                color = self.intakeRunColors

            # Configure LEDs
            if blink:
                self.led.strobe(
                    color if type(color) == list else [color],
                    self.strobeDurationSlow.get() if slow else self.strobeDurationFast.get()
                )
            else:
                self.led.solid( color )
        else:
            self.led.solid( self.invalidColors )

    def setIntakeIsRunning(self, function:typing.Callable[[],bool] = lambda: False):
        self.intakeIsRunning = function

    def setIntakeHasNote(self, function:typing.Callable[[],bool] = lambda: False):
        self.intakeHasNote = function

    def setIndexerHasNote(self, function:typing.Callable[[],bool] = lambda: False):
        self.indexerHasNote = function

    def setPivotAutoAdjust(self, function:typing.Callable[[],bool] = lambda: False):
        self.pivotAutoAdjust = function

    def setPivotAtSetpoint(self, function:typing.Callable[[],bool] = lambda: False):
        self.pivotAtSetpoint = function

    def setLaunchRotation(self, function:typing.Callable[[],bool] = lambda: False):
        self.launchAimGood = function

    def setLaunchRangeFar(self, function:typing.Callable[[],bool] = lambda: False):
        self.launchRangeFar = function

    def setLaunchRangeNear(self, function:typing.Callable[[],bool] = lambda: False):
        self.launchRangeNear = function

    def setLaunchRangeAuto(self, function:typing.Callable[[],bool] = lambda: False):
        self.launchRangeAuto = function

    def setIsEndgame(self, function:typing.Callable[[],bool] = lambda: False):
        self.isEndgame = function

    def runDistraction(self):
        self.led.strobe( self.distractionColors, self.strobeDurationFast.get() )

    def runStaleyCelebration(self):
        timer = Timer.getFPGATimestamp()
        x = timer % 6.0 / 6.0
        if x > 0.5:
            self.led.stripes( self.staleyColors, duration = self.stripesDurationFast.get() )
        else: 
            self.led.strobe( self.staleyColors, self.strobeDurationSlow.get() )
