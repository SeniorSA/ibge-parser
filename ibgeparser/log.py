from logzero import logger, logfile
import os

DEBUG = False 

def init():
    pasta_log = '{}/logs'.format(os.getcwd())
    if not os.path.exists(pasta_log):
        os.makedirs(pasta_log)

    logfile('{}/ibge_parser.log'.format(pasta_log), maxBytes=1e6, backupCount=3)

def exception(e):
    logger.exception(e)

def info(s):
    logger.info(s)

def error(s):
    logger.error(s)

def debug(s):
    if DEBUG:
        logger.debug(s)