import time
from os import path


def create_logger(address):
    log_name = str(time.time()) + '---' + address[0] + '---#' + str(address[1])
    absolute_path = path.dirname(path.abspath(__file__))
    log_address = path.join(absolute_path, 'logs')
    log = open(path.join(log_address, log_name), 'w')
    return log


def write_log(logger, message):
    logger.write(message)


def close_log(logger):
    logger.close()
