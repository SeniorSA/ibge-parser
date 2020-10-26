from logzero import logger, logfile
import os

DEBUG = False

class _Log:
    def init(self):
        pasta_log = os.path.join(os.getcwd(),'logs')
        if not os.path.exists(pasta_log):
            os.makedirs(pasta_log)

        arquivo_log = os.path.join(pasta_log,'ibge_parser.log')
        logfile(arquivo_log, maxBytes=1e6, backupCount=3)

        self.debug('Logs estão salvos em: {}'.format(arquivo_log))

    def exception(self, e):
        logger.exception(e)

    def info(self, s):
        logger.info(s)

    def error(self, s):
        logger.error(s)

    def debug(self, s):
        if DEBUG:
            logger.debug(s)