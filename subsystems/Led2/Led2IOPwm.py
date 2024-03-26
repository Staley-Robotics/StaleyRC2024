from typing import overload
from wpilib import RobotState, AddressableLED, Color, Timer

from util import *
from .Led2IO import Led2IO

class Led2IOPwm(Led2IO):
    def __init__(self, PWMPort:int):
        # Tunables
        self.ledLength = NTTunableInt( "/Config/Led/Length", 22, updater=self.configureBuffer, persistent = True )
        self.strobeDuration = NTTunableFloat( "/Config/Led/DefaultEffects/Strobe/Duration", 0.5, persistent = True )
        self.breatheDuration = NTTunableFloat( "/Config/Led/DefaultEffects/Breathe/Duration", 1.0, persistent = True )
        self.rainbowDuration = NTTunableFloat( "/Config/Led/DefaultEffects/Rainbow/Duration", 1.0, persistent = True )
        self.rainbowBrightness = NTTunableInt( "/Config/Led/DefaultEffects/Rainbow/Brightness", 255, persistent = True )
        self.waveDuration = NTTunableFloat( "/Config/Led/DefaultEffects/Wave/Duration", 1.0, persistent = True )
        self.stripesDuration = NTTunableFloat( "/Config/Led/DefaultEffects/Stripes/Duration", 1.0, persistent = True )
        self.waveExponent = NTTunableFloat( "/Config/Led/DefaultEffects/Wave/Exponent", 0.4, persistent = True )

        # Logging
        #self.ledLogger = NetworkTableInstance.getDefault().getStructTopic( "/LED", LedIO.LedIOInputs ).publish()

        ## init LED
        self.m_led = AddressableLED( PWMPort )
        self.m_buffer = []
        self.configureBuffer()

    def updateInputs(self, inputs:Led2IO.Led2IOInputs): pass

    def run(self):
        self.m_led.setData( self.m_buffer )

    def configureBuffer(self):
        length = self.ledLength.get()
        # Error Check for Valid Value
        if 0 < length <= 5460:
            length = min( max( length, 1 ), 5460 )
            self.ledLength.set( length )

        # Configure LED Buffer
        self.m_led.stop()
        self.m_led.setLength( length )
        self.m_buffer = [AddressableLED.LEDData() for i in range(length)]
        self.m_led.setData( self.m_buffer )
        self.m_led.start()

    def run(self) -> None:
        self.m_led.setData( self.m_buffer )

    def solid(self, color:Color):
        for i in range( self.ledLength.get() ):
            self.m_buffer[i].setLED( color )
    
    def strobe(self, colors:list[Color], duration:float=0.0):
        # Input Validation
        if duration <= 0.0: duration = self.strobeDuration.get()
        if len(colors) < 2:
            colors.append( Color.kBlack )

        i = int(Timer.getFPGATimestamp() % duration / duration * len(colors))
        self.solid( colors[i] )

    def breathe(self, c1:Color, c2:Color, duration:float=0.0 ):
        # Input Validation
        if duration == 0.0: duration = self.breatheDuration.get()
        
        time = Timer.getFPGATimestamp()

        x = time % duration / duration * 2.0 * math.pi
        ratio = (math.sin(x) + 1.0) / 2.0

        red = (c1.red * (1 - ratio)) + (c2.red * ratio)
        green = (c1.green * (1 - ratio)) + (c2.green * ratio)
        blue = (c1.blue * (1 - ratio)) + (c2.blue * ratio)

        self.solid( Color( red, green, blue) )

    def rainbow(self, cycleLength:float, duration:float=0.0):
        # Input Validation
        if cycleLength < 1: cycleLength = len( self.m_buffer )
        if duration == 0.0: duration = self.rainbowDuration.get()

        # Brightness Input Validation
        brightness = self.rainbowBrightness.get()
        if 0 <= brightness <= 255:
            brightness = min( max( brightness, 0 ), 255 )
            self.rainbowBrightness.set( brightness )

        time = Timer.getFPGATimestamp()
        length = len( self.m_buffer )
        
        x = ( 1 - ((time / duration % 1.0)) * 180.0 )
        xDiffPerLed = 180.0 / cycleLength
        for i in range(length):
            x += xDiffPerLed
            x %= 180.0
            self.m_buffer[i].setHSV( int(x), brightness, brightness )

    def wave(self, c1:Color, c2:Color, cycleLength:float, duration:float=0.0):
        # Input Validation
        if cycleLength < 1: cycleLength = len( self.m_buffer )
        if duration == 0.0: duration = self.waveDuration.get()
        
        time = Timer.getFPGATimestamp()
        length = len(self.m_buffer)
        waveExp = self.waveExponent.get()

        x = (1 - ((time % duration) / duration)) * 2.0 * math.pi
        xDiffPerLed = 2.0 * math.pi / cycleLength
        for i in range(length):
            x += xDiffPerLed
            try:
                ratio = (math.pow(math.sin(x), waveExp) + 1.0) / 2.0
            except ValueError:
                try:
                    ratio = (-math.pow(math.sin(x + math.pi), waveExp) + 1.0) / 2.0
                except ValueError:
                    ratio = 0.5
            red = (c1.red * (1 - ratio)) + (c2.red * ratio)
            green = (c1.green * (1 - ratio)) + (c2.green * ratio)
            blue = (c1.blue * (1 - ratio)) + (c2.blue * ratio)
            self.m_buffer[i].setLED( Color(red,green,blue) )

    def stripes(self, colors:list[Color], start:int=0, length:int=0, duration:float=0.0):
        # Input Validation
        if start < 0: start = 0
        if length <= 0:
            length = len(self.m_buffer)
        if duration <= 0.0: duration = self.stripesDuration.get()
        # Error Check for Oversized Length
        if start + length > len(self.m_buffer):
            length = len(self.m_buffer) - start

        time = Timer.getFPGATimestamp()

        offset = int( time % duration / duration * length * len(colors) )
        for i in range(length):
            idx = i + start
            colorIdx = int( math.floor( float( (idx - offset)/length ) + len(colors) ) % len(colors) )
            colorIdx = len(colors) - 1 - colorIdx
            self.m_buffer[idx].setLED( colors[colorIdx] )