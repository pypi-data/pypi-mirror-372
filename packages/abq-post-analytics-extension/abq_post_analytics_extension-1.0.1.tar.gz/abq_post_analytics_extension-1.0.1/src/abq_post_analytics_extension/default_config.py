# -*- coding: UTF-8 -*-
from collections import OrderedDict

default_config_dict = OrderedDict({
    "logging": {
        "logger_name": "abq_post_analytics_extension",
        "logger_path": None,
        "general_level": "debug",
        "stream_level": "warning",
        "file_level": "info",
        "logger_formatter": "%(asctime)s\t%(name)s\t%(levelname)s\t%(filename)s at line %(lineno)d\t%(message)s"
    },
    "command_line_progress_monitor": {
        "content_width": 118,
        "progress_interval": 0.1
    },
})
