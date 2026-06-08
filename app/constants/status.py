from enum import StrEnum


class CartStatus(StrEnum):
    ACTIVE = "ACTIVE"
    CHECKED_OUT = "CHECKED_OUT"
    ABANDONED = "ABANDONED"
