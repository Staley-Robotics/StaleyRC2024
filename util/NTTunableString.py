import typing
from ntcore import *

class NTTunableString:
    table:str = None
    name:str = None
    value:str = 0.0
    callable:typing.Callable[[],None] = lambda: None
    persistent:bool = False

    def __init__( self,
                  name:str,
                  value:str,
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
            self.value = str(value)
        else:
            raise TypeError( f"{self.name} is not of type String.  Please verify the appropriate NetworkTable Entry Type and try again." )
        
        # Clear Persistent Flag if requested
        if not persistent:
            ntTbl.clearPersistent( self.name )

        # Add Listener
        ntInst.addListener(
            [f"/Tunable/{self.name}"],
            EventFlags.kValueAll,
            self.update
        )

    def get(self) -> str:
        """
        """
        return str(self.value)
    
    def update(self, event:Event) -> None:
        """
        """
        # Get the updated value from the Event
        try:
            value = str( event.data.value.value() )
        except Exception as e:
            pass
        
        # Validate Value
        if type(self.value) is str:
            # Update Value in Memory and Update Configuration
            self.value = value
            self.callable()
        else:
            # Value is invalid, return value to standard
            ntTbl = NetworkTableInstance.getDefault().getTable("Tunable")
            if not ntTbl.putNumber( self.name, self.value ):
                raise TypeError( f"{self.name} is not of type String.  Please verify the appropriate NetworkTable Entry Type and try again." )