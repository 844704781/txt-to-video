from processor.abstract_processor import AbstractProcessor
from processor.runway_txt_processor import RunWayTxtParser
from processor.runway_img_processor import RunWayImgParser
from processor.runway_mix_processor import RunWayMixParser
from processor.pika_txt_processor import PikaTxtAbstractProcessor
from processor.pika_img_processor import PikaImgProcessor
from processor.pika_mix_processor import PikaMixProcessor
from entity.iconfig_parser import ConfigParser
from entity.video_const import VideoConst


class VideoBuilder:

    def __init__(self):
        self._video = None
        self._config = None
        self._content = None
        self._image = None

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

    def set_form(self, content: str, image: str):
        self._content = content
        self._image = image
        return self

    def build(self) -> AbstractProcessor:

        if self.video == VideoConst.RUN_WAY_TXT:

            return RunWayTxtParser(self.config.username, self.config.password, VideoConst.RUN_WAY_TXT) \
                .set_form(self._content, self._image)
        elif self.video == VideoConst.RUN_WAY_IMG:

            return RunWayImgParser(self.config.username, self.config.password, VideoConst.RUN_WAY_TXT) \
                .set_form(self._content, self._image)
        elif self.video == VideoConst.RUN_WAY_MIX:

            return RunWayMixParser(self.config.username, self.config.password, VideoConst.RUN_WAY_MIX) \
                .set_form(self._content, self._image)
        elif self.video == VideoConst.PIKA_TXT:

            return PikaTxtAbstractProcessor(self.config.username, self.config.password, VideoConst.PIKA_TXT) \
                .set_form(self._content, self._image)
        elif self.video == VideoConst.PIKA_IMG:

            return PikaImgProcessor(self.config.username, self.config.password, VideoConst.PIKA_IMG) \
                .set_form(self._content, self._image)
        elif self.video == VideoConst.PIKA_MIX:

            return PikaMixProcessor(self.config.username, self.config.password, VideoConst.PIKA_MIX) \
                .set_form(self._content, self._image)
        else:
            raise Exception("无效的VideoProcessor")
