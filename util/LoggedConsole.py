import io
import sys
import typing

from wpilib import reportError
from ntcore import NetworkTableInstance

class LoggedConsole:
    def getNewData(self) -> str:
        return ""
    
    def periodic(self) -> None:
        data = self.getNewData()
        if data != "":
            NetworkTableInstance.getDefault().getTable("Logging").putString(
                "Console", data
            )

class LoggedConsoleRIO(LoggedConsole):
    filePath = "/home/lvuser/FRC_UserProgram.log"
    reader = None

    def __init__(self):
        try:
            self.reader = io.TextIOWrapper( io.FileIO(self.filePath, "r") )
        except FileNotFoundError as e:
            reportError( f"Failed to open console file {self.filePath}", True )

    def getNewData(self) -> str:
        if self.reader == None:
            return ""
        
        newData = ""
        try:
            readlines = self.reader.readlines()
            for x in range(len(readlines)):
                newData += readlines[x]
        except Exception as e:
            reportError( f"Failed to read from console file {self.filePath}", True )
        
        return newData

    def close(self) -> None:
        self.reader.close()

class LoggedConsoleSIM(LoggedConsole):
    class SplitTextIO(typing.IO):
        def __init__(self, *streams:typing.IO):
            self.streams = streams

        def write(self, data):
            for stream in self.streams:
                stream.write(data)

    originalStdout:typing.TextIO = None #PrintStream
    originalStderr:typing.TextIO = None #PrintStream
    customStdout:io.StringIO = io.StringIO()
    customStderr:io.StringIO = io.StringIO()
    customStdoutPos:int = 0
    customStderrPos:int = 0

    def __init__(self):
        self.originalStdout = sys.stdout
        self.originalStderr = sys.stderr
        sys.stdout = self.SplitTextIO( self.originalStdout, self.customStdout )
        sys.stderr = self.SplitTextIO( self.originalStderr, self.customStderr )

    def getNewData(self) -> str:
        fullStdoutStr:str = self.customStdout.getvalue()
        if fullStdoutStr == None:
            fullStdoutStr = ""
        newStdoutStr:str = fullStdoutStr[self.customStdoutPos:]
        self.customStdoutPos = len(fullStdoutStr)
        fullStderrStr:str = self.customStderr.getvalue()
        if fullStderrStr == None:
            fullStderrStr = ""
        newStderrStr:str = fullStderrStr[self.customStderrPos:]
        self.customStderrPos = len(fullStderrStr)

        return newStdoutStr + newStderrStr

    def close(self) -> None:
        sys.stdout = self.originalStdout
        sys.stderr = self.originalStderr
