# Module Name: strategies/copy/huggingface.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2024 WattleFlow
# License: Apache 2 Licence
# Description: This modul contains concrete huggingface strategy classes.

import os
import logging
import shutil
from wattleflow.core import IStrategy
from transformers.file_utils import TRANSFORMERS_CACHE

size = lambda p: int(os.path.getsize(p) / 1024)

logger = logging.getLogger("[huggingface.helper]")
logger.setLevel(logging.info)
logger.debug(f"Size: {size}")


class StrategyCopyHuggingfaceModels(IStrategy):
    def file_size(path):
        size = os.path.getsize(path) / 1024
        decimal = int(size - int(size))

        for unit in ["KB", "MB", "GB", "TB"]:
            if size < 1024:
                logging.debug("size < 1024")
                break
            size /= 1024

        if not int(size) > 0:
            return "0 KB"

        decimal = size - int(size)

        return (
            "{0:.2f} {1}".format(size, unit)
            if decimal > 0.0
            else "{0} {1}".format(int(size), unit)
        )

    def execute(
        self, source_dir: str = TRANSFORMERS_CACHE, destination_dir: str = None
    ):
        if not os.path.exists(source_dir):
            logger.error(f"Source directory not found: {source_dir}' ne postoji.")
            return

        if not os.path.exists(destination_dir):
            logger.info("Creating directory: {}".format(destination_dir))
            os.makedirs(destination_dir)

        for root, dirs, files in os.walk(source_dir):
            relative_path = os.path.relpath(root, source_dir)
            target_dir = os.path.join(destination_dir, relative_path)

            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            for file in files:
                source_path = os.path.join(root, file)
                target_path = os.path.join(target_dir, file)
                basename = os.path.basename(source_path)
                dirname = os.path.dirname(target_path)

                logger.info(
                    'Copying "{}" [{}]'.format(basename, self.file_size(source_path))
                )

                if os.path.exists(target_path):
                    if os.path.samefile(source_path, target_path):
                        logger.warning("File exist: {target_path}")
                        break

                shutil.copy2(source_path, target_path)
                logger.info(f"Kopirano: {basename} -> {dirname}")

        logger.info("Copying done.")
