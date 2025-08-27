# Module Name: helpers/audit.py
# Description: This modul contains helpers audit handling class.
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2025 WattleFlow
# License: Apache 2 Licence

# import asyncio
# import logging
# from logging.handlers import QueueHandler
# from abc import ABC, abstractmethod
# from typing import Optional


# class AsyncAuditHandler(logging.Handler):
#     def __init__(self, queue):
#         super().__init__()
#         self.queue = queue

#     def emit(self, record):
#         try:
#             log_entry = self.format(record)
#             self.queue.put_nowait(log_entry)
#         except Exception:
#             self.handleError(record)


# def setup_logging():
#     queue = asyncio.Queue()
#     logger = logging.getLogger("GlobalLogger")
#     logger.setLevel(logging.DEBUG)

#     audit_handler = AsyncAuditHandler(queue)
#     formatter = logging.Formatter(
#         "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
#     )
#     audit_handler.setFormatter(formatter)
#     logger.addHandler(audit_handler)
#     return logger, queue
