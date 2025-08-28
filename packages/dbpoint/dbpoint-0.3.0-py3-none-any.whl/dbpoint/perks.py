import sys
from loguru import logger
   
def halt(code: int, message: str):
    """
    Shortcut (for serious error situations) for logging message and do quick exit 
    Be aware: for Airflow any return code (incl 0) means that task is failed (dont use halt on normal flow!)
    For other running systems (bash script etc) You can control flow using exit code (regular end is code 0 automatically)
    Exit code must by between 0 and 255. Any other cases we will map to 255 
    """
    code = code if code >= 0 and code <= 255 else 255
    logger.error(f"{code} {message}")
    sys.exit(code)
