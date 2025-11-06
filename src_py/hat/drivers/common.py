import enum


class CommLogAction(enum.Enum):
    OPEN = 'open'
    CLOSE = 'close'
    SEND = 'send'
    RECEIVE = 'receive'
