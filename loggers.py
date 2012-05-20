'''
A module to create and share a few logging instances
'''

import logging
import os

'''
Hacky method of importing the settings module that is currently
running.

The way this works is by detecting the environment setting for
the settings module which Django loads (we load it in the case
of apache) and then uses that setting as the string name, we
then build a list of module level variable names which we want
to import, set up both dicts to insert them from/to then put it
into the name space of _mod_.
'''
settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
fromset = ["ROOT_LOG_DIR", "LOGLEVEL"]
_mod_ = __import__(settings_module, globals(), locals(), fromset, -1)

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
    logger.setLevel(_mod_.LOGLEVEL)
    fh = logging.FileHandler(os.path.join(root_path, filename + '.log'))
    fh.setFormatter(frmt)
    logger.addHandler(fh)
    return logger

database_log = create_logger('database', root_path=_mod_.ROOT_LOG_DIR)
email_log = create_logger('email', root_path=_mod_.ROOT_LOG_DIR)
debug_log = create_logger('debug', root_path=_mod_.ROOT_LOG_DIR)
info_log = create_logger('info', root_path=_mod_.ROOT_LOG_DIR)
error_log = create_logger('error', root_path=_mod_.ROOT_LOG_DIR)
suspicious_log = create_logger('suspicious', root_path=_mod_.ROOT_LOG_DIR)

if __name__ == '__main__':
    # test the logs
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
