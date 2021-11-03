import logging
from utils.customlog import StreamToLogger, CustomLoggerLevels
from  utils.filepath import log_path
import sys

def setup_logging(args, level):
    logging.setLoggerClass(CustomLoggerLevels)

    import datetime
    current_time = datetime.datetime.today().strftime("%d-%m-%y_%H:%M:%S")
    if args.logfile is not None:
        logging.basicConfig(
            filename=log_path + f"/{current_time}.log",
            level=level,  # lvl 15 is DETAIL
            format="[%(asctime)s] %(name)s/%(module)s/%(levelname)s: %(message)s",
            datefmt="%d-%m %H:%M:%S",
        )
        # redirect stdout
        stdout_logger = logging.getLogger("STDOUT")
        sl = StreamToLogger(stdout_logger, logging.INFO)
        sys.stdout = sl
        # redirect sterr
        stderr_logger = logging.getLogger("STDERR")
        sl = StreamToLogger(stderr_logger, logging.ERROR)
        sys.stderr = sl
    else:
        logging.basicConfig(
            level=level,  # lvl 15 is DETAIL
            format="[%(asctime)s][%(module)s/%(levelname)s]: %(message)s",
            datefmt="%d-%b %H:%M:%S",
        )
    logger = logging.getLogger("MAIN")
    logger.info("Program Startup")

    def log_detail(*args, **kwdargs):
        logger.log(15, *args, **kwdargs)

    # ? logger.detail is a custom logging level used instead of DEBUG (for most things that are not spammers), so that it hides other things DEBUG messages in the logs
    logger.detail = log_detail
    
    return logger