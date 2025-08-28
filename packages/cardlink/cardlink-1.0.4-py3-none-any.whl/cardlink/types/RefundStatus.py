from enum import Enum


class RefundStatus(Enum):
    """Статус возврата"""

    new = "NEW"
    process = "PROCESS"
    success = "SUCCESS"
    fail = "FAIL"
