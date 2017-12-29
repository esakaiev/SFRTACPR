import logging
import logging.config
import os

LOGGER_CFG = r'logging.conf'


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Logger(object):
    __metaclass__ = Singleton

    def __init__(self, email='esakaiev@redhat.com'):
        self.logger = logging.getLogger('simple_example')
        self._set_logger_handlers()
        self.email = email

    def _set_logger_handlers(self):
        self.logger.setLevel(logging.DEBUG)

        handlers = [logging.FileHandler('log_output.log', 'w'), logging.StreamHandler()]

        for handler in handlers:
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(fmt='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log(self, module_path, status, message):
        if status == 'PASS' or status == 'FAIL' or status == 'INFO':
            self.logger.info("[{0}] - [{1}] - [{2}]".format(module_path, status, message))
        elif status == 'ERROR':
            self.logger.error("[{0}] - [{1}] - [{2}]".format(module_path, status, message))
        elif status == 'WARNING':
            self.logger.warning("[{0}] - [{1}] - [{2}]".format(module_path, status, message))
        elif status == 'DEBUG':
            self.logger.debug("[{0}] - [{1}] - [{2}]".format(module_path, status, message))
        else:
            raise Exception(
                "Wrong log status format, should be one of the following: ['PASS', 'FAIL', 'ERROR', 'INFO', 'DEBUG', 'WARNING']")

    def send_email(self):
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.utils import COMMASPACE, formatdate
        # to send

        msg = MIMEMultipart()
        msg['From'] = 'esakaiev@redhat.com'
        msg['To'] = 'esakaiev@redhat.com'
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'test'

        mailer = smtplib.SMTP('127.0.0.1')
        mailer.connect()
        mailer.sendmail('somebody@redhat.com', 'esakaiev@reshat.com', msg.as_string())
        mailer.close()


if __name__ == '__main__':
    logger = Logger('email')
    module_path = os.path.abspath(__file__)
    logger.log(module_path, "DEBUG", "asdnvkabsdv")
    logger.log(module_path, "PASS", "asdnvkabsdv")
    logger.log(module_path, "FAIL", "asdnvkabsdv")
    logger.log(module_path, "WARNING", "asdnvkabsdv")
    logger.log(module_path, "INFO", "asdnvkabsdv")
