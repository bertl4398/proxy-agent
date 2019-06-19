import socket
import logging

from tasks import celery, sock


logger = logging.getLogger()


@celery.task()
def block_ip(ip, port):
    cmd = "BLK tcp {} {}".format(ip, port).encode("utf-8")
    logger.debug("Sending {!r}".format(cmd))
    try:
        sock.sendall(cmd)

        amount_received = 0
        amount_expected = len(cmd)

        while amount_received < amount_expected:
            data = sock.recv(1024)
            amount_received += len(data)
            logger.debug("received {!r}".format(data))
    except socket.error as error:
        logger.error(error)
    return cmd.decode("utf-8")
