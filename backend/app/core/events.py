from enum import Enum


class EventType(str, Enum):
    STATUS = "status"
    NODE = "node"
    TABLE = "table"
    SUMMARY = "summary"
    ERROR = "error"
    DONE = "done"


class CrawlPhase(str, Enum):
    QUEUED = "queued"
    NAVIGATING = "navigating"
    EXTRACTING = "extracting"
    SUMMARIZING = "summarizing"
    FINISHED = "finished"
