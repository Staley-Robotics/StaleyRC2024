# import typing

# import commands2

# from subsystems._Pivot import *


# class pointToStick(commands2.command.Command):
#     def __init__(self,
#                   pivot:Pivot,
#                   trigger_axis:typing.Callable[[], float],
#                   ):
#         super().__init__()

#         self.pivot = pivot

#         self.trigger = trigger_axis
    
#     def initialize(self):
#         return super().initialize()
#     def execute(self):
        

#         return super().execute()
#     def end(self, interrupted: bool):
#         return super().end(interrupted)
    
#     def isFinished(self) -> bool:
#         return False