import argparse
import os
import pandas
import feedback_record
import download_center
import analysis_center
import logging

def parse_excel_file(file_name):
    if not os.path.exists(file_name):
        return []
    
    data = pandas.read_excel(file_name, index_col=0)

    records = []
    for index, row in data.iterrows():
        record = feedback_record.FeedbackRecord(row)
        records.append(record)

    return records

def main():
    # Initialize parser
    parser = argparse.ArgumentParser()
    
    # Adding optional argument
    parser.add_argument("-f", "--file", 
                        help="Please input a file name as an parameter!", required=True)
    
    parser.add_argument("-d", "--download", 
                        help="Please input the concurrent size of download pool!", required=False, 
                        default=1, type=int)
    
    parser.add_argument("-a", "--analysis", 
                        help="Please input the concurrent size of analysis pool!", required=False, 
                        default=1, type=int)
    
    # Read arguments from command line
    args = parser.parse_args()
    logging.info(args.file)
    records = parse_excel_file(args.file)
    if len(records) <= 0:
        logging.info("No Record was Found. Please try again.")
        return
    
    download_tasks = []
    for record in records:
        download_tasks.append(record.get_download_task())

    log_download_center = download_center.DownloadCenter(args.download)
    log_analysis_center = analysis_center.AnalysisCenter(args.analysis)
    log_analysis_center.start_process()

    log_download_center.register_callback(log_analysis_center)
    log_download_center.start_download(download_tasks)
 
    log_analysis_center.stop_process()
    log_analysis_center.output()

if __name__ == '__main__':
    logging.basicConfig(
                format='%(asctime)s %(levelname)s %(process)d %(filename)s %(message)s',
                level=logging.INFO,
                datefmt='%Y-%m-%d %H:%M:%S')
    main()