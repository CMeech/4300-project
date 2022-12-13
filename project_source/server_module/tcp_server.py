#
# tcp_server.py
#
# AUTHOR: Cassius Meeches
#
# PURPOSE: Implements an RSocket TCP server connection.
#
import asyncio
import logging
from project_source.common.constants import LOCALHOST
from project_source.common.messages import SERVING

from project_source.server_module.server_handler import ServerHandler
from rsocket.rsocket_server import RSocketServer
from rsocket.transports.tcp import TransportTCP


#
# TCPServer
#
# PURPOSE: Initializes a socket using TCP and runs the file
# transfer server on top of it.
#
class TCPServer:
    async def run_server(self, address: str, server_port: int):
        logging.info(SERVING.format(address, server_port))

        def session(*connection):
            RSocketServer(TransportTCP(*connection), handler_factory=ServerHandler)

        # We're actually giving TCP an advantage here since there is no TLS. 
        # Will note in the results.
        server = await asyncio.start_server(session, address, server_port)

        async with server:
            await server.serve_forever()
