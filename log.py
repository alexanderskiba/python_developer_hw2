import logging
import functools

# Определим логгер
def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fileHandler = logging.FileHandler(log_file, 'w')
    fileHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)


setup_logger('info_logger', 'info.log', logging.INFO)
setup_logger('error_logger', 'error.log', logging.ERROR)

logger_info = logging.getLogger('info_logger')
logger_error = logging.getLogger('error_logger')

def logging_decor(func):
    @functools.wraps(func)
    def decorated(self,*args):
            try:
                result = func(self, *args)
            except TypeError as ex:
                logger_error.error("TypeError {0}".format(ex))
                raise ex
            except ValueError as ex:
                logger_error.error("ValueError {0}".format(ex))
                raise ex
            except AttributeError as ex:
                logger_error.error("Попытка изменить имя или фамилию {0}".format(ex))
                raise ex
            names_dict = {'__init__': 'Создан объект','__set__':'Изменено' }
            logger_info.info(f'{names_dict[func.__name__]} {args}')
            return result
    return decorated
