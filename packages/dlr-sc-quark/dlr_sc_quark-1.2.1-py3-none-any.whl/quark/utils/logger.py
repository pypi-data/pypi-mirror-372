# Copyright 2022 DLR-SC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" module for helper functions for logging """

import os
import logging
from types import MethodType


LOG_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"


def get_logger(logger_name,
               log_level=logging.INFO,
               log_level_console=logging.INFO,
               log_level_file=logging.NOTSET,
               log_file=None,
               log_folder=None):
    """
     get the default logger

    :param (str) logger_name: name of the logger, if already present, overwrite
    :param (logging.level) log_level: threshold log level
    :param (logging.level) log_level_console: log level for console logging, use logging.NOTSET to disable
    :param (logging.level) log_level_file: log level for file logging, use logging.NOTSET to disable
    :param (str) log_file: path to log file, by default logger_name with suffix .log
                           only applicable if log_level_file is not logging.NOTSET,
    :param (str) log_folder: if given, the full log file path is created by concatenating log_folder and log_file,
                             create folder if not existent, only applicable if log_level_file is not logging.NOTSET
    :return: the logger
    """
    logger = logging.getLogger(logger_name)
    # add close_all_handlers function to logger
    logger.close_all_handlers = MethodType(close_all_handlers, logger)
    # close all handlers (in case logger was used before)
    logger.close_all_handlers()

    logger.setLevel(log_level)
    formatter = logging.Formatter(LOG_FORMAT)

    # configure console handler
    if log_level_console != logging.NOTSET:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level_console)
        logger.addHandler(console_handler)

    # configure file handler
    if log_level_file != logging.NOTSET:
        # configure log file
        # set log file to logger_name if none is given
        if log_file is None:
            log_file = logger_name + ".log"
        # create logging folder if log_folder option is given
        if log_folder:
            if not os.path.exists(log_folder):
                os.makedirs(log_folder)
            # prepend log_folder to log_file
            log_file = log_folder + "/" + log_file

        # configure handler
        file_handler = logging.FileHandler(log_file, mode="w")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level_file)
        logger.addHandler(file_handler)

    return logger

def close_all_handlers(logger):
    """
    close all handlers of logger

    :param (logging.Logger) logger: logger to close all handlers
    """
    handlers = list(logger.handlers)
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)
