'''
A module to create and share a few logging instances
'''

import logging
import os
try:
    from timetracker.settings import LOGLEVEL
except:
    LOGLEVEL = logging.DEBUG

# Where you want the logs to go
ROOT_DIR = '/home/xeno/log/timetracker/'

def create_logger(filename,
                  level=logging.DEBUG,
                  root_path=os.path.dirname(__file__)):
    '''
    Creates and returns a logger instance
    '''
    frmt = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(filename)
    logger.setLevel(LOGLEVEL)
    fh = logging.FileHandler(os.path.join(root_path, filename+'.log'))
    fh.setFormatter(frmt)
    logger.addHandler(fh)
    return logger

database_log = create_logger('database', root_path=ROOT_DIR)
email_log = create_logger('email', root_path=ROOT_DIR)
debug_log = create_logger('debug', root_path=ROOT_DIR)
info_log = create_logger('info', root_path=ROOT_DIR)
error_log = create_logger('error', root_path=ROOT_DIR)
if __name__ == '__main__':
    database_log.debug('hello')
    database_log.info('hello')
    database_log.warn('hello')
    database_log.critical('hello')
    database_log.error('hello')

    email_log.debug('hello')
    email_log.info('hello')
    email_log.warn('hello')
    email_log.critical('hello')
    email_log.error('hello')

    debug_log.debug('hello')
    debug_log.info('hello')
    debug_log.warn('hello')
    debug_log.critical('hello')
    debug_log.error('hello')

    info_log.debug('hello')
    info_log.info('hello')
    info_log.warn('hello')
    info_log.critical('hello')
    info_log.error('hello')

    error_log.debug('hello')
    error_log.info('hello')
    error_log.warn('hello')
    error_log.critical('hello')
    error_log.error('hello')
