from io import BufferedReader, FileIO
import typing

from wpilib import DriverStation

class Console:
    def getNewData(self):
        raise NotImplementedError

class ConsoleRIO(Console):
    filePath = "/home/lvuser/FRC_UserProgram.log"
    reader = None

    bufferSize:int = 10240
    writePosition = 0
    data:typing.Tuple[bytes] = bytes[bufferSize]

    def __init__(self):
        try:
            self.reader = BufferedReader( FileIO(self.filePath, "r") )
        except FileNotFoundError as e:
            DriverStation.reportError( f"Failed to open console file {self.filePath}", True )


    def getNewData(self) -> str:
        if self.reader == None:
            return
        
        while True:
            nextChar:int = -1
            try:
                nextChar = self.reader.read()
            except Exception as e:
                DriverStation.reportError( f"Failed to read from console file {self.filePath}", True )
            
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

class ConsoleSIM(Console):
    from io import BufferedReader, FileIO
    from wpilib import DriverStation

    def __init__(self):
        pass

    def getNewData(self):
        pass

    def close(self) -> None:
        pass