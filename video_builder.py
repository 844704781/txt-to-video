from processor.abstract_processor import AbstractProcessor
from processor.runway_txt_processor import RunWayTxtParser
from entity.iconfig_parser import ConfigParser
from entity.video_const import VideoConst


class VideoBuilder:

    def __init__(self):
        self._video = None
        self._config = None
        self._tips = None

    @staticmethod
    def create():
        return VideoBuilder()

    @property
    def video(self):
        return self._video

    @property
    def config(self):
        return self._config

    def set_processor(self, video: str):
        self._video = video
        return self

    def set_config(self, config: ConfigParser):
        self._config = config
        return self

    def set_tips(self, tips: str):
        self._tips = tips
        return self

    def build(self) -> AbstractProcessor:
        if self.video == VideoConst.RUN_WAY:
            p = RunWayTxtParser(self.config.username, self.config.password, VideoConst.RUN_WAY)
            p.set_tips(self._tips)
            return p
        elif self.video == VideoConst.mro():
            return None
        else:
            raise Exception("无效的VideoProcessor")
