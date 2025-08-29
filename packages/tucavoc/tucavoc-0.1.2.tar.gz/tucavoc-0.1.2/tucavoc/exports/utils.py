import enum


class QAFlags(enum.Enum):
    VALID = 0.000
    INVALID = 0.999
    BELOW_DETECTION_LIMIT = 0.147
    LOCAL_CONTAMINATION = 0.559
