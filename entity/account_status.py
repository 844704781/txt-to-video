from enum import IntEnum


class AccountStatus(IntEnum):
    NORMAL = 1  # 正常
    EXCEPTION = 5  # 异常
    DISABLED = 9  # 余额不足
