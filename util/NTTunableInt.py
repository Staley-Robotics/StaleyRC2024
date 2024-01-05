import typing
from ntcore import *

class NTTunableInt:
    table:str = None
    name:str = None
    value:int = 0.0
    callable:typing.Callable[[],None] = lambda: None
    persistent:bool = False

    def __init__( self,
                  name:str,
                  value:int,
                  callable:typing.Callable[[],None] = lambda: None,
                  persistent:bool = False
                ) -> None:
        """
        """
        # Save Global Variables
        self.name = name
        self.value = value
        self.callable = callable

        # Get Network Tables
        ntInst = NetworkTableInstance.getDefault()
        ntTbl = ntInst.getTable("Tunable")
        
        if ntTbl.setDefaultNumber(self.name, value):
            self.value = int(value)
            # Set Persistent Flag if requested
            if persistent:
                ntTbl.setPersistent( self.name )
        else:
            self.value = int( ntTbl.getNumber( self.name ) )

        # Clear Persistent Flag if requested
        if not persistent:
            ntTbl.clearPersistent( self.name )

        # Add Listener
        ntInst.addListener(
            [f"/Tunable/{self.name}"],
            EventFlags.kValueAll,
            self.update
        )

    def get(self) -> int:
        """
        """
        return int(self.value)
    
    def update(self, event:Event) -> None:
        """
        """
        # Get the updated value from the Event
        try:
            value = int( event.data.value.value() )
        except Exception as e:
            pass
        
        # Validate Value
        if type(self.value) is int:
            # Update Value in Memory and Update Configuration
            self.value = value
            self.callable()
        else:
            # Value is invalid, return value to standard
            ntTbl = NetworkTableInstance.getDefault().getTable("Tunable")
            if not ntTbl.putNumber( self.name, self.value ):
                raise TypeError( f"{self.name} is not of type Int.  Please verify the appropriate NetworkTable Entry Type and try again." )
