class FeedbackRecord(object):
    def __init__(self, row):
        self._row = row
        self._feedback_id = row["反馈ID"]
        self._log_url = row["日志"]

    def get_feedback_id(self):
        return self._feedback_id
    
    def get_log_url(self):
        return self._log_url

    def __str__(self):
        str = "反馈ID: {0}\n反馈内容: {1}\n具体问题(用户): {2}\n问题发生时间: {3}\nROM版本: {4}\n"
        return str.format(self._feedback_id, 
                   self._row["反馈内容"],
                   self._row["问题类型(用户)"],
                   self._row["问题发生时间"],
                   self._row["ROM版本"])
    
    def get_download_task(self):
        return {
            "url": self._log_url,
            "name": str(self._feedback_id) + ".zip",
            "id": self._feedback_id,
            "record": self
        }
