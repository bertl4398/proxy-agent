import socket
import logging

from celery import Celery

import config


logger = logging.getLogger()


def make_celery():
    celery = Celery(__name__, broker=config.CELERY_BROKER)
    celery.conf.update(config.as_dict())

    uds_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        uds_socket.connect(config.AGENT_SOCK)
    except socket.error as error:
        logger.warning(error)

    return celery, uds_socket


celery, sock = make_celery()
