# 🔍 Parallel Log Analyzer with Multiprocessing and KMP Matching

A high-performance, Python-based log analysis tool designed for large-scale mobile system logs.  
It supports concurrent processing using `multiprocessing.Pool`, flexible keyword matching powered by the **KMP (Knuth-Morris-Pratt)** algorithm, and race-condition-safe inter-process coordination.

---

##  Features

-  **Parallel Processing** — Efficient log analysis across multiple CPU cores
-  **Fast Keyword Matching** — Optimized with the KMP algorithm (`O(n + m)` complexity)
-  **Multiprocessing Safe** — Uses `Lock()` and `Manager().dict()` to avoid duplicate processing
-  **Automatic Decompression** — Handles nested ZIP archives
-  **Configurable Analysis Tasks** — Driven by JSON-based task configuration
-  **30%+ performance boost** over legacy single-threaded tools

---

##  Project Structure

log-analyzer/
- ├── analysis_center.py        # Task controller: multiprocessing, queue handling
- ├── analysis_task.py          # Task logic: decompress, scan, and match files using KMP
- ├── config.json               # Sample task configuration (keywords, file patterns)
- ├── download_center.py        # Simulated callback for receiving downloaded logs
- ├── download_test.py          # Script for testing file downloads
- ├── feedback_record.py        # Record structure for feedback/log metadata
- ├── log_tools.py              # Utility functions for log processing
- ├── multithreading.py         # Comparison module (threading vs multiprocessing)
- └── README.md                 # Project documentation
## 🔬 How It Works

###  Decompression
- Automatically extracts ZIP files, including nested archives.
- Caches decompressed results to avoid redundant I/O operations.

###  Parallel Task Execution
- Utilizes `multiprocessing.Pool` to execute log scanning tasks in parallel.
- Each process fetches tasks from a shared `Queue`.
- Significantly boosts performance compared to single-threaded processing.

###  KMP-Based Matching
- Replaces naive `str.find()` with the **KMP (Knuth-Morris-Pratt)** pattern matching algorithm.
- Reduces time complexity from **O(n × m)** to **O(n + m)**.
- Optimized for large-scale logs with gigabytes of data.

###  Duplicate Prevention & Synchronization
- Uses `multiprocessing.Manager().dict()` to track processed files across processes.
- Applies `Lock()` to safely manage shared state (like result lists or file status flags).
- Prevents redundant file analysis and avoids race conditions in multi-process environments.
