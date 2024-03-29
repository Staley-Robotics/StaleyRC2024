import commands2

from commands import *
from sequences.NoteToss import NoteToss
from sequences.NoteLaunchSpeaker import NoteLaunchSpeaker
from sequences.NoteLoadGround import NoteLoadGround
from subsystems import Intake, Indexer, Pivot, Launcher
from util import *

class NoteAction(commands2.ConditionalCommand):
    def __init__(self, intake:Intake, indexer:Indexer, launcher:Launcher, pivot:Pivot, launchCalc:LaunchCalc):
        super().__init__(
            NoteLaunchSpeaker(indexer, launcher, pivot, launchCalc),
            NoteLoadGround(intake, indexer, pivot),
            indexer.hasNote
        )

    def initialize(self):
        super().initialize()
        self.setName( self.selectedCommand.getName() )
        