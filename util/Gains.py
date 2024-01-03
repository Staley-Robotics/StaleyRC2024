import ntcore
import wpiutil

class Gains(wpiutil.Sendable):
    kP = 0.0
    kI = 0.0
    kD = 0.0
    kF = 0.0

    def __init__(self, kP:float = 0.0, kI:float = 0.0, kD:float = 0.0, kF:float = 0.0):
        self.setPIDF( kP, kI, kD, kF )

    def setPIDF( self, kP:float = 0.0, kI:float = 0.0, kD:float = 0.0, kF:float = 0.0 ):
        self.setP( kP )
        self.setI( kI )
        self.setD( kD )
        self.setF( kF )

    def setP( self, kP:float = 0.0 ):
        self.kP = kP

    def setI( self, kI:float = 0.0 ):
        self.kI = kI

    def setD( self, kD:float = 0.0 ):
        self.kD = kD

    def setF( self, kF:float = 0.0 ):
        self.kF = kF

    def initSendable(self, builder:ntcore.NTSendableBuilder):
        builder.setSmartDashboardType( "RobotPreferences" )
        self._builder = builder
