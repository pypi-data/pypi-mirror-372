import enum


class QueueProcessStatus(enum.StrEnum):
    SUCCESS = "success"
    FATAL = "fatal"
    WARNING = "warning"
