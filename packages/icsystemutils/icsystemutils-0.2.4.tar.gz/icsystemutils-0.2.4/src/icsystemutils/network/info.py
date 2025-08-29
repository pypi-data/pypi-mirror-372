import socket

from iccore.system.network.info import NetworkInfo


def load() -> NetworkInfo:
    hostname = socket.gethostname()
    return NetworkInfo(hostname=hostname)
