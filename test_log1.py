# import logging
# logging.basicConfig(filename='example.log', level=logging.DEBUG)
# logging.debug('This message should go to the log file')
# logging.info('So should this')
# logging.warning('And this, too')

import logging
from test_log2 import haha

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename="classical_planning.log",
                    filemode="w",
                    format=LOG_FORMAT,
                    datefmt=DATE_FORMAT,
                    level=logging.DEBUG)
a = 5
logging.debug(f'This is a debug message{a}')
logging.info('This is an info message')
logging.warning('This is a warning message')
logging.error('This is an error message')
logging.critical('This is a critical message')

haha()
