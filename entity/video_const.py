from db.taskdb import Source
from entity.task_make_type import MakeType


class VideoConst:
    RUN_WAY_TXT = "RUN_WAY_TXT"
    RUN_WAY_IMG = "RUN_WAY_IMG"
    RUN_WAY_MIX = "RUN_WAY_MIX"
    PIKA_TXT = "PIKA_TXT"
    PIKA_IMG = "PIKA_IMG"
    PIKA_MIX = "PIKA_MIX"


def transfer(source, make_type):
    if source == Source.RUN_WAY:
        if make_type == MakeType.MIX:
            return VideoConst.RUN_WAY_MIX
        elif make_type == MakeType.IMAGE:
            return VideoConst.RUN_WAY_IMG
        else:
            return VideoConst.RUN_WAY_TXT
    else:
        if make_type == MakeType.MIX:
            return VideoConst.PIKA_MIX
        elif make_type == MakeType.IMAGE:
            return VideoConst.PIKA_IMG
        else:
            return VideoConst.PIKA_TXT
