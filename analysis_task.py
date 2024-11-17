import json
import os
import zipfile
import logging
import glob

LOG_CACHE_FOLDER = "cache"

class AnalysisTask:
    def __init__(self, next_task):
        self._next_task = next_task
        self._results = []

    def process(self, context):
        if self._next_task:
            self._results += self._next_task.process(context)
        return self._results

class DecompressTask(AnalysisTask):
    def __init__(self, next_task):
        super().__init__(next_task)
    
    def process(self, context):
        if not os.path.exists(LOG_CACHE_FOLDER):
            os.makedirs(LOG_CACHE_FOLDER)

        logging.info("DecompressTask. Context: {0}".format(context))
        directory_to_extract_to = os.path.join(LOG_CACHE_FOLDER, str(context["id"]))
        logging.info("DecompressTask. Path: {0}".format(directory_to_extract_to))

        if os.path.exists(directory_to_extract_to):
            logging.info("Found Cache: {0}. Ignore Decompress.".format(directory_to_extract_to))
        else:
            logging.info("Not foud Cache: {0}. Decompress. {1}".format(directory_to_extract_to, context["path"]))
            with zipfile.ZipFile(context["path"], 'r') as zip_ref:
                zip_ref.extractall(directory_to_extract_to)

            extension = ".zip"
            for item in os.listdir(directory_to_extract_to): # loop through items in dir
                item = os.path.join(directory_to_extract_to, item)
                logging.debug(os.path.abspath(item))
                if item.endswith(extension): # check for ".zip" extension
                    file_name = os.path.abspath(item) # get full path of files
                    zip_ref = zipfile.ZipFile(file_name) # create zipfile object
                    zip_ref.extractall(directory_to_extract_to) # extract file to dir
                    zip_ref.close() # close file
                    os.remove(file_name)
        context["work_folder"] = directory_to_extract_to
        return super().process(context)
    
class GroupTask(AnalysisTask):
    def __init__(self, next_task):
        super().__init__(next_task)
        self._tasks = []
    
    def add_task(self, task):
        self._tasks.append(task)
    
    def process(self, context):
        for task in self._tasks:
            self._results += task.process(context)
        return super().process(context)
    
class ScanFileTask(AnalysisTask):
    def __init__(self, next_task):
        super().__init__(next_task)

    def process(self, context):
        logging.info("ScanFileTask Process, Param: {0}".format(self._match_params))
        return super().process(context)
    
    def setup(self, context, scan_task_config):
        self._match_params = scan_task_config["match_params"]
        self._scan_task_config = scan_task_config
        group_task = GroupTask(self._next_task)

        for file_task_config in scan_task_config["log_files"]:
            file_task = FileTask(None)
            file_task.setup(context, file_task_config)
            group_task.add_task(file_task)

        self._next_task = group_task

class FileTask(AnalysisTask):
    def __init__(self, next_task):
        super().__init__(next_task)
    
    def setup(self, context, file_task_config):
        self._file_process_tasks = []
        self._file_task_config = file_task_config
        
        for tool in file_task_config["tools"]:
            # TODO: Add more file process task
            file_process_task = FileProcessTask(None)
            file_process_task.setup(context, tool["params"])
            self._file_process_tasks.append(file_process_task)
    
    def search_files(self, context):
        key = self._file_task_config["name"]
        search_path = os.path.join(context["work_folder"], key)

        logging.info("Search Folder: {0}, Key: {1}".format(context["work_folder"], key))
        filenames = []
        for file in glob.iglob(search_path, recursive=True):
            if os.path.isfile(file):
                filenames.append(file)
        logging.info("Search Folder: {0}, Files:  {1}".format(search_path, filenames))
        return filenames
    
    def process(self, context):
        files = self.search_files(context)
        if not files or len(files) <= 0:
            return super().process(context)

        logging.info("FileTask, Found files: {0}".format(files))
        for file in files:
            f = open(file, 'rt', errors='ignore')
            lines = f.readlines()
            f.close()

            for task in self._file_process_tasks:
                task.attach_file_lines(file, lines)
                self._results += task.process(context)
        return super().process(context)
    
class FileProcessTask(AnalysisTask):
    def __init__(self, next_task):
        super().__init__(next_task)

    def setup(self, context, params):
        self._params = params

    def attach_file_lines(self, file, lines):
        self._file = file
        self._lines = lines

    def process(self, context):
        # logging.info("FileProcessTask {0}".format(self._params))
        result = []
        # result.append("FileProcessTask Reslt, Start.File: {0}\n".format(self._file))
        for line in self._lines:
            for param in self._params:
                if line.find(param) != -1:
                    result.append(line)
                    # logging.info("Output: {0}".format(line))
        # result.append("FileProcessTask Reslt, End\n")
        self._results += result
        return super().process(context)
    
class AnalysisTaskFactory:
    def __init__(self, config):
        self._config_path = config
        self.load_config()

    def load_config(self):
        if not os.path.exists(self._config_path):
            raise Exception("Analysis Configure is not found. Please check.")
        f = open(self._config_path, "r")
        self._configs = json.loads(f.read())
        f.close()

    def construct_decompress_task(self, context):
        return DecompressTask(None)

    def construct_task(self, context):
        group_task = GroupTask(None)
        for scan_file_task_config in self._configs:
            file_task = ScanFileTask(None)
            file_task.setup(context, scan_file_task_config)
            group_task.add_task(file_task)
        return group_task
    
    def contruct_tool(self, tool):
        if tool["name"] == "":
            return
    
    def query_file_task(self):
        pass
