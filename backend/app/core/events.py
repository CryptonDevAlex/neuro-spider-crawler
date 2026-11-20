from enum import Enum


class EventType(str, Enum):
    STATUS = "status"
    NODE = "node"
    FINDING = "finding"
    SUMMARY = "summary"
    ERROR = "error"
    DONE = "done"


class ScanPhase(str, Enum):
    QUEUED = "queued"
    DISCOVERING = "discovering"
    ANALYZING = "analyzing"
    REPORTING = "reporting"
    FINISHED = "finished"
