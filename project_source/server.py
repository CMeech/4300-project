#
# server.py
#
# AUTHOR: Cassius Meeches
#
# PURPOSE: Implements the main program for the server
# application.
#
import asyncio
import logging
import sys
from project_source.common.constants import DEBUG, MAIN, QUIC, TCP
from project_source.common.messages import MISSING_ARGS, SERVER_ERROR
from project_source.database.queries import initialize_database

from project_source.server_module.tcp_server import TCPServer
from project_source.server_module.quic_server import QUICServer


def run_quic_server(address: str, server_port: int):
    server = QUICServer()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.run_server(address, server_port))
    try:
        initialize_database()
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    except Exception:
        logging.error(SERVER_ERROR)


def run_tcp_server(address: str, server_port: int):
    server = TCPServer()
    try:
        initialize_database()
        asyncio.run(server.run_server(address, server_port))
    except Exception:
        logging.error(SERVER_ERROR)


def main():
    if len(sys.argv) < 4:
        print(MISSING_ARGS)
        exit()

    # parse the arguments
    address = sys.argv[1]
    port = sys.argv[2]
    type = sys.argv[3]
    debug = sys.argv[4]

    # show debug log
    if debug == DEBUG:
        logging.basicConfig(filename="server.log", level=logging.DEBUG)

    if type == QUIC:
        run_quic_server(address=address, server_port=port)
    elif type == TCP:
        run_tcp_server(address=address, server_port=port)


if __name__ == MAIN:
    main()
