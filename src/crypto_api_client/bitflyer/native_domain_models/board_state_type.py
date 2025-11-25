from __future__ import annotations

from enum import Enum


class BoardStateType(Enum):
    RUNNING = "RUNNING"
    CLOSED = "CLOSED"
    STARTING = "STARTING"
    PREOPEN = "PREOPEN"
    CIRCUIT_BREAK = "CIRCUIT BREAK"
