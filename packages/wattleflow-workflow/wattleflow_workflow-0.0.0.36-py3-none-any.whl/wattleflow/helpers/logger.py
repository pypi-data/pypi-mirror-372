# Module Name: helpers/logger.py
# Description: This modul contains logger helper classes.
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2024 WattleFlow
# License: Apache 2 Licence

# import logging
# import asyncio
# from logging.handlers import QueueHandler, QueueListener
# from queue import Queue
# from concurrent.futures import ThreadPoolExecutor

# class AsyncHandler(logging.Handler):
#     def __init__(self, queue):
#         super().__init__()
#         self.queue = queue

#     def emit(self, record):
#         try:
#             self.queue.put_nowait(self.format(record))
#         except Exception:
#             self.handleError(record)

# async def log_writer(queue):
#     while True:
#         log_message = await queue.get()
#         if log_message == "exit":
#             break
#         print(log_message)

# def setup_logging():
#     queue = asyncio.Queue()
#     queue_handler = AsyncHandler(queue)
#     logger = logging.getLogger("concurrent.futures")  # Koristite specifičan naziv logera
#     logger.setLevel(logging.DEBUG)
#     logger.addHandler(queue_handler)
#     return queue, logger

# def run_task():
#     logger = logging.getLogger("concurrent.futures")
#     logger.debug("Debug poruka iz futures")

# # Glavna funkcija
# async def main():
#     queue, logger = setup_logging()

#     # Pokretanje log_writer korutine
#     log_task = asyncio.create_task(log_writer(queue))

#     # Koristimo ThreadPoolExecutor za pokretanje zadataka u niti
#     with ThreadPoolExecutor() as executor:
#         for _ in range(5):
#             executor.submit(run_task)

#     # Zatvaranje log writer-a
#     await queue.put("exit")
#     await log_task

# # Pokretanje aplikacije
# asyncio.run(main())
