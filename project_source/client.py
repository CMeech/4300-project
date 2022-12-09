import asyncio
import logging
import sys
from project_source.common.constants import DEBUG, MAIN, QUIC, TCP
from project_source.common.messages import MISSING_ARGS

from project_source.client_module.tcp_client import TCPClient
from project_source.client_module.quic_client import QUICClient

def main():
    if len(sys.argv) < 5:
        print(MISSING_ARGS)
        exit()

    # add IP later
    address = sys.argv[1]
    port = sys.argv[2]
    type = sys.argv[3]
    username = sys.argv[4]
    debug = sys.argv[5]

    # show debug log
    if debug == DEBUG:
        logging.basicConfig(filename="client.log", level=logging.DEBUG)

    client = None
    if type == QUIC:
        client = QUICClient()
    elif type == TCP:
        client = TCPClient()

    asyncio.run(client.connect(address=address,server_port=port, username=username))

if __name__ == MAIN:
    main()
