#
# tcp_client.py
#
# AUTHOR: Cassius Meeches
#
# PURPOSE: Implements an RSocket TCP client connection.
#
import asyncio
import logging

from project_source.client_module.client_task import run_client
from rsocket.helpers import single_transport_provider
from rsocket.rsocket_client import RSocketClient
from rsocket.transports.tcp import TransportTCP

from project_source.common.messages import CONNECTING


#
# TCPClient
#
# PURPOSE: Initializes a socket using TCP and runs the file
# transfer application on top of it.
#
class TCPClient:

    async def connect(self, address: str, server_port: int, username: str):
        logging.info(CONNECTING.format(address, server_port))

        connection = await asyncio.open_connection(address, server_port)

        async with RSocketClient(single_transport_provider(TransportTCP(*connection))) as client:
            await run_client(client, username)
