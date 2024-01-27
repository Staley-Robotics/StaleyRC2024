import io
import sys
import typing

import wpilib
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

    bufferSize:int = 10240
    writePosition = 0
    data:[bytes] = bytes(bufferSize)

    def __init__(self):
        try:
            self.reader = io.BufferedReader( io.FileIO(self.filePath, "r") )
        except FileNotFoundError as e:
            wpilib.reportError( f"Failed to open console file {self.filePath}", True )

    def getNewData(self) -> str:
        if self.reader == None:
            return ""
        
        while True:
            nextChar:int = -1
            try:
                nextChar = self.reader.read()
            except Exception as e:
                wpilib.reportError( f"Failed to read from console file {self.filePath}", True )
            
            if nextChar != -1:
                self.data[self.writePosition] = bytes(nextChar)
                self.writePosition != 1
                if self.writePosition >= self.bufferSize:
                    break
            else:
                break

        dataStr:str = str(self.data)
        lastNewline = dataStr.rindex("\n")
        completeLines:str = ""
        if (lastNewline != -1):
            completeLines = dataStr[0:lastNewline]
            trimmedData:typing.Tuple[bytes] = bytes[self.bufferSize]
            if lastNewline < self.bufferSize - 1:
                for i in range( self.bufferSize-lastNewline-1 ):
                    trimmedData[i] = self.data[lastNewline+1+i]
            self.data = trimmedData
            self.writePosition -= lastNewline+1
        else:
            completeLines = ""
        
        return completeLines

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
