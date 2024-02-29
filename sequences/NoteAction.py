import commands2

from commands import *
from sequences.NoteLaunchSpeaker import NoteLaunchSpeaker
from sequences.NoteLoadGround import NoteLoadGround
from subsystems import Intake, Indexer, Pivot, Elevator, Launcher
from util import *

class NoteAction(commands2.ConditionalCommand):
    def __init__(self, intake:Intake, indexer:Indexer, launcher:Launcher, pivot:Pivot, elevator:Elevator):
        super().__init__(
            NoteLaunchSpeaker(indexer, launcher, pivot, elevator),
            NoteLoadGround(intake, indexer, pivot, elevator),
            indexer.hasNote
        )

    def initialize(self):
        super().initialize()
        self.setName( self.selectedCommand.getName() )
        