import datetime
import warnings
import traceback
import runpy

class CoolLog:
    _DEFAULT_KEY = "\033["
    _LOG_FILE = "logs.txt"

    _COLORS = {
        "ERROR": "31",    
        "WARNING": "33",  
        "SUCCESS": "32",  
        "INFO": "34",     
        "DEBUG": "35",    
        "CRITICAL": "41", 
    }

    @staticmethod
    def _write_log(level: str, message: str):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color = CoolLog._COLORS.get(level, "0")

        label = f"{CoolLog._DEFAULT_KEY}2;{color}m[{level}-{timestamp}]{CoolLog._DEFAULT_KEY}0m"

        text = f"{CoolLog._DEFAULT_KEY}1;{color}m{message}{CoolLog._DEFAULT_KEY}0m"

        print(f"{label} {text}")

        file_text = f"[{level}-{timestamp}] {message}\n"
        with open(CoolLog._LOG_FILE, "a", encoding="utf-8") as f:
            f.write(file_text)

    @staticmethod
    def error(message: str):
        CoolLog._write_log("ERROR", message)

    @staticmethod
    def warning(message: str):
        CoolLog._write_log("WARNING", message)

    @staticmethod
    def success(message: str):
        CoolLog._write_log("SUCCESS", message)

    @staticmethod
    def info(message: str):
        CoolLog._write_log("INFO", message)

    @staticmethod
    def debug(message: str):
        CoolLog._write_log("DEBUG", message)

    @staticmethod
    def critical(message: str):
        CoolLog._write_log("CRITICAL", message)

    @staticmethod
    def auto_log(filename: str):
        CoolLog.info(f"Starting execution of '{filename}'")

        def warn_handler(message, category, filename, lineno, file=None, line=None):
            CoolLog.warning(f"[line-{lineno}] {message}")

        warnings.showwarning = warn_handler

        try:
            runpy.run_path(filename)
            CoolLog.success(f"File '{filename}' executed successfully.")
        except SyntaxError as e:
            CoolLog.critical(f"[line-{e.lineno}] {e.msg}")
            CoolLog.debug(f"File: {e.filename}, Offset: {e.offset}")
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            if tb:
                last = tb[-1]
                line = last.lineno
                CoolLog.error(f"[line-{line}] {e}")
                CoolLog.debug("Traceback (most recent call last):")
                for frame in tb:
                    CoolLog.debug(f"  File '{frame.filename}', line {frame.lineno}, in {frame.name}")
            else:
                CoolLog.error(str(e))

