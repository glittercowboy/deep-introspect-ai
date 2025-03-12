"""
Logging configuration for the application.
"""
import logging
import sys
from pathlib import Path
from loguru import logger
import json

# Configure loguru logger
class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        Intercept log records from logging and pass them to loguru
        """
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where the logged message was emitted
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

class JsonSink:
    """Custom JSON sink for structured logging"""
    def __init__(self, file_path):
        self.file_path = file_path
    
    def __call__(self, message):
        record = message.record
        
        # Basic log data
        data = {
            "time": record["time"].isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "file": record["file"].name,
            "function": record["function"],
            "line": record["line"],
        }
        
        # Add exception info if present
        if record["exception"]:
            data["exception"] = str(record["exception"])
        
        # Add extra attributes
        if record["extra"]:
            data["extra"] = record["extra"]
        
        # Write to file
        with open(self.file_path, "a") as f:
            f.write(json.dumps(data) + "\n")

def configure_logging():
    """Configure logging with loguru"""
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)
    
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True,
    )
    
    # Add file handler for all logs
    logger.add(
        log_path / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="1 week",
    )
    
    # Add JSON file handler for structured logging
    logger.add(
        JsonSink(log_path / "app.json.log"),
        level="INFO",
        serialize=True,
    )
    
    # Add handler for error logs
    logger.add(
        log_path / "error.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB",
        retention="1 month",
    )
    
    # Intercept standard library logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Update logging levels for some modules
    for logger_name in ("uvicorn", "uvicorn.error", "fastapi"):
        logging.getLogger(logger_name).handlers = [InterceptHandler()]
        
    # Set log level for specific loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    return logger