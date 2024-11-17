import sys, os
import zipfile
import urllib.request
from multiprocessing import Pool
from functools import partial
import logging

DOWNLOAD_FOLDER = "download"

class DownlaodFinishedCallback(object):
    def on_receive_file(self, task):
        logging.info("Please implement the on_receive_file callback")
        pass

class DownloadCenter(object):
    def __init__(self, concurrent=1):
        self._concurrent = concurrent
        self._callbacks = []

    def register_callback(self, callback):
        self._callbacks.append(callback)

    def unregister_callback(self, callback):
        pass

    def start_download(self, tasks):
        logging.info("Concurrent Pool Size: {0} ".format(self._concurrent))

        if not os.path.exists(DOWNLOAD_FOLDER):
            os.makedirs(DOWNLOAD_FOLDER)
        
        pool = Pool(self._concurrent)
        download_func = partial(self.download)
        pool.map(download_func, tasks)
        pool.close()
        pool.join()

        logging.info("All files downloaded. Close download center.")

    def download(self, task):
        # TODO: 支持断点续传，检测当前文件是否符合条件
        logging.basicConfig(
                format='%(asctime)s %(levelname)s %(process)d %(filename)s %(message)s',
                level=logging.INFO,
                datefmt='%Y-%m-%d %H:%M:%S')
        
        path = os.path.join(DOWNLOAD_FOLDER, task["name"])
        if os.path.exists(path):
            task["path"] = path
            logging.info("{0} exists. Ignore download".format(task["name"]))
            return self.dispatch_file(task)

        try:
            urllib.request.urlretrieve(task["url"], path)
            task["path"] = path
            logging.info(" Downloaded {} ".format(task["name"]))
        except Exception as e:
            logging.info(e)
            return False

        return self.dispatch_file(task)

    
    def dispatch_file(self, task):
        for callback in self._callbacks:
            callback.on_receive_file(task)
        return True
    