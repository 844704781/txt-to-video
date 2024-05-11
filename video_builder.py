from processor.abstract_processor import AbstractProcessor
from processor.runway_txt_processor import RunWayTxtParser
from processor.runway_img_processor import RunWayImgParser
from processor.runway_mix_processor import RunWayMixParser
from processor.pika_txt_processor import PikaTxtAbstractProcessor
from processor.pika_img_processor import PikaImgProcessor
from processor.pika_mix_processor import PikaMixProcessor
from entity.iconfig_parser import ConfigParser
from entity.video_const import VideoConst

from typing import Optional, Callable


class VideoBuilder:

    def __init__(self):
        self._progress_callback = None
        self._balance_callback = None
        self._check_task_callback = None
        self._video = None
        self._config = None
        self._content = None
        self._image = None
        self._task_id = None

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

    def set_task_id(self, task_id: str):
        self._task_id = task_id
        return self

    def set_config(self, config: ConfigParser):
        self._config = config
        return self

    def set_form(self, content: str, image: str):
        self._content = content
        self._image = image
        return self

    def progress_callback(self, callback: object = None):
        self._progress_callback = callback
        return self

    def set_balance_callback(self, callback: object = None):
        self._balance_callback = callback
        return self

    def set_check_task_callback(self, callback: object = None):
        self._check_task_callback = callback
        return self

    def build(self) -> AbstractProcessor:

        if self.video == VideoConst.RUN_WAY_TXT:

            return RunWayTxtParser(self.config.username, self.config.password, VideoConst.RUN_WAY_TXT, self._task_id) \
                .set_form(self._content, self._image).set_progress_callback(
                self._progress_callback).set_balance_callback(self._balance_callback).set_check_task_callback(
                self._check_task_callback)
        elif self.video == VideoConst.RUN_WAY_IMG:

            return RunWayImgParser(self.config.username, self.config.password, VideoConst.RUN_WAY_TXT, self._task_id) \
                .set_form(self._content, self._image).set_progress_callback(
                self._progress_callback).set_balance_callback(self._balance_callback).set_check_task_callback(
                self._check_task_callback)
        elif self.video == VideoConst.RUN_WAY_MIX:

            return RunWayMixParser(self.config.username, self.config.password, VideoConst.RUN_WAY_MIX, self._task_id) \
                .set_form(self._content, self._image).set_progress_callback(
                self._progress_callback).set_balance_callback(self._balance_callback).set_check_task_callback(
                self._check_task_callback)
        elif self.video == VideoConst.PIKA_TXT:

            return PikaTxtAbstractProcessor(self.config.username, self.config.password, VideoConst.PIKA_TXT,
                                            self._task_id) \
                .set_form(self._content, self._image).set_progress_callback(
                self._progress_callback).set_balance_callback(self._balance_callback).set_check_task_callback(
                self._check_task_callback)
        elif self.video == VideoConst.PIKA_IMG:

            return PikaImgProcessor(self.config.username, self.config.password, VideoConst.PIKA_IMG, self._task_id) \
                .set_form(self._content, self._image).set_progress_callback(
                self._progress_callback).set_balance_callback(self._balance_callback).set_check_task_callback(
                self._check_task_callback)
        elif self.video == VideoConst.PIKA_MIX:

            return PikaMixProcessor(self.config.username, self.config.password, VideoConst.PIKA_MIX, self._task_id) \
                .set_form(self._content, self._image).set_progress_callback(
                self._progress_callback).set_balance_callback(self._balance_callback).set_check_task_callback(
                self._check_task_callback)
        else:
            raise Exception("无效的VideoProcessor")
