import download_center
import os
from multiprocessing import Pool
from functools import partial
from multiprocessing import Queue, Manager
import time
import random
import analysis_task
import logging
import datetime

LOG_CACHE_FOLDER = "cache"
END_QUEUE_MESSAGE = "CANCEL"

class AnalysisCenter(download_center.DownlaodFinishedCallback):
    def __init__(self, concurrent=1, config="config.json"):
        self._concurrent = concurrent
        self._waitting_task = False
        self._queue = Manager().Queue()
        self._analysistask_factory = analysis_task.AnalysisTaskFactory(config)
        self._results = []

    def on_receive_file(self, task):
        logging.info("Receive task from callback. Task: {0}".format(task))
        self._queue.put(task)

    def stop_process(self):
        self._waitting_task = False
        self._queue.put("CANCEL")
        self.wait_finish()

    def start_process(self):
        self._waitting_task = True

        logging.info("Start analysis..., Waitinig files..., Concurrent: {0}".format(self._concurrent))
        self._pool = Pool(self._concurrent)
        process_func = partial(self.process)

        def receive_result(result):
            self._results.append(result)

        results = self._pool.apply_async(process_func, callback=receive_result)
        logging.info(results)

    def process(self):
        logging.basicConfig(
                format='%(asctime)s %(levelname)s %(process)d %(filename)s %(message)s',
                level=logging.INFO,
                datefmt='%Y-%m-%d %H:%M:%S')
        
        logging.info("Start analysis...")
        results = []
        try:
            while self._waitting_task or not self._queue.empty():
                context = self._queue.get(True, timeout=300)
                if context == END_QUEUE_MESSAGE:
                    logging.info("Receve Quit Message, Quit Worker.")
                    break
                logging.info("Receive task: ", context)

                # Decompress first
                try:
                    decompress_task = self._analysistask_factory.construct_decompress_task(context)
                    output = decompress_task.process(context)
                    logging.info("Finish decompress task: {0}".format(output))
                except Exception as e:
                    logging.error("Finish decompress task faiiled: {0}".format(e))

                try:
                    task = self._analysistask_factory.construct_task(context)
                    output = task.process(context)
                    results.append(
                        {
                            "id": context["record"].get_feedback_id(),
                            "record": context["record"],
                            "result": output
                        }
                    )
                    logging.info("Finish process task.")
                except Exception as e:
                    logging.error("Finish process task faiiled: {0}".format(e))
                
                time.sleep(1)
        except Exception as e:
            logging.error(e)
            logging.error("Wait Task Timeout, Quit.")
        return results

    def wait_finish(self):
        logging.info("Waitting analysis...")
        self._pool.close()
        self._pool.join()
        logging.info("End analysis.")

    def receive_result(self):
        logging.info("Receive Result...")

    def output(self):
        # merge multiple process result
        results = []
        for result in self._results:
            results += result

        def sort_record(val):
            return val["id"]
        
        results.sort(key=sort_record)
        f = open("result-{0}.txt".format(datetime.datetime.now()), "wt")
        for result in results:
            output_result = []
            output_result.append(str(result["record"]))
            output_result += result["result"]
            output_result.append("===============================================\n")
            output_result.append("===============================================\n")
            f.writelines(output_result)
        f.close()
        
    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['_pool']
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)