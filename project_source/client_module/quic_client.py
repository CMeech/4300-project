#
# quic_client
#
# PURPOSE: Implements a QUIC RSocket client connection.
#

import logging
from pathlib import Path

from aioquic.quic.configuration import QuicConfiguration

from project_source.client_module.client_task import run_client
from rsocket.helpers import single_transport_provider
from rsocket.rsocket_client import RSocketClient
from rsocket.transports.aioquic_transport import rsocket_connect

from project_source.common.constants import LOCALHOST
from project_source.common.messages import CONNECTING

CA_FILE_PATH = '../certificates/pycacert.pem'


class QUICClient:

    async def connect(self, address: str, server_port: int, username: str):
        logging.info(CONNECTING.format(address, server_port))

        client_configuration = QuicConfiguration(
            is_client=True,
            idle_timeout=600
        )
        client_configuration.load_verify_locations(cafile=str(CA_FILE_PATH))

        async with rsocket_connect(address, server_port,
                                  configuration=client_configuration) as transport:
            async with RSocketClient(single_transport_provider(transport)) as client:
                await run_client(client, username)
