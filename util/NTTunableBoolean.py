import typing
from ntcore import *

class NTTunableBoolean:
    table:str = None
    name:str = None
    value:bool = False
    callable:typing.Callable[[],None] = lambda: None
    persistent:bool = False

    def __init__( self,
                  name:str,
                  value:bool,
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
        
        if ntTbl.setDefaultBoolean(self.name, value):
            self.value = value
            # Set Persistent Flag if requested
            if persistent:
                ntTbl.setPersistent( self.name )
        else:
            self.value = bool( ntTbl.getBoolean( self.name, value ) )
        
        # Clear Persistent Flag if requested
        if not persistent:
            ntTbl.clearPersistent( self.name )

        # Add Listener
        ntInst.addListener(
            [f"/Tunable/{self.name}"],
            EventFlags.kValueAll,
            self.update
        )

    def get(self) -> bool:
        """
        """
        return bool(self.value)

    def set(self, value:bool) -> None:
        """
        """
        ntInst = NetworkTableInstance.getDefault()
        ntTbl = ntInst.getTable("Tunable")
        if ntTbl.putBoolean( self.name, value ):
            self.value = value
    
    def update(self, event:Event) -> None:
        """
        """
        # Get the updated value from the Event
        try:
            value = bool( event.data.value.value() )
        except Exception as e:
            pass
        
        # Validate Value
        if type(self.value) is bool:
            # Update Value in Memory and Update Configuration
            self.value = value
            self.callable()
        else:
            # Value is invalid, return value to standard
            ntTbl = NetworkTableInstance.getDefault().getTable("Tunable")
            if not ntTbl.putBoolean( self.name, self.value ):
                raise TypeError( f"{self.name} is not of type Boolean.  Please verify the appropriate NetworkTable Entry Type and try again." )
