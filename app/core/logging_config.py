# app/core/logging_config.py

import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
from pathlib import Path
from datetime import datetime

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
APP_NAME = "salepie"

def get_log_dir():
    env_dir = os.getenv("LOG_DIR")
    if env_dir:
        return Path(env_dir)
    return Path("logs")

# ✅ เพิ่มฟังก์ชันนี้เพื่อจัด Format ชื่อไฟล์ตอน Rotate
def namer(name):
    # name ที่รับมาจะเป็น: logs/salepie.log.2026-02-13
    # เราจะแก้เป็น: logs/salepie.2026-02-13.log
    return name.replace(".log", "") + ".log"

def setup_logging():
    # 1. Prepare Directory
    log_dir = get_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)

    # 2. Fix Filename (❌ เอาวันที่ออกจากชื่อไฟล์ตั้งต้น)
    # ให้ชื่อไฟล์ปัจจุบันเป็นชื่อกลางๆ เสมอ เพื่อให้ดูง่ายว่าไฟล์ไหนคือไฟล์ล่าสุด
    filename_clean = f"{APP_NAME}.log" 
    log_file_path = log_dir / filename_clean

    formatter = logging.Formatter(LOG_FORMAT)

    # 3. File Handler
    file_handler = TimedRotatingFileHandler(
        filename=str(log_file_path),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    
    # กำหนดรูปแบบวันที่ที่จะต่อท้าย (เช่น 2026-02-13)
    file_handler.suffix = "%Y-%m-%d"
    
    # ✅ ใส่ namer เพื่อย้าย .log ไปไว้ท้ายสุด
    file_handler.namer = namer
    
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 4. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # 5. Apply to ROOT Logger
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    
    if root.handlers:
        root.handlers.clear()
        
    root.addHandler(file_handler)
    root.addHandler(console_handler)
    
    # 6. Override Uvicorn/FastAPI Loggers
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        _log = logging.getLogger(logger_name)
        _log.handlers = [file_handler, console_handler]
        _log.propagate = False

    print(f"\n[LOG SETUP] Writing logs to: {log_file_path}")