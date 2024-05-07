from processor.abstract_processor import AbstractProcessor
from processor.runway_txt_processor import RunWayTxtParser
from processor.runway_img_processor import RunWayImgParser
from processor.pika_txt_processor import PikaTxtAbstractProcessor
from entity.iconfig_parser import ConfigParser
from entity.video_const import VideoConst


class VideoBuilder:

    def __init__(self):
        self._video = None
        self._config = None
        self._content = None

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

    def set_content(self, content: str):
        self._content = content
        return self

    def build(self) -> AbstractProcessor:

        if self.video == VideoConst.RUN_WAY_TXT:
            return RunWayTxtParser(self.config.username, self.config.password, VideoConst.RUN_WAY_TXT) \
                .set_content(self._content)
        elif self.video == VideoConst.RUN_WAY_IMG:
            return RunWayImgParser(self.config.username, self.config.password, VideoConst.RUN_WAY_TXT) \
                .set_content(self._content)
        elif self.video == VideoConst.PIKA_TXT:
            return PikaTxtAbstractProcessor(self.config.username, self.config.password, VideoConst.PIKA_TXT) \
                .set_content(self._content)
        else:
            raise Exception("无效的VideoProcessor")
