import logging
from project_source.common.constants import LOCALHOST
from project_source.common.messages import SERVING

from project_source.server_module.server_handler import ServerHandler
from aioquic.quic.configuration import QuicConfiguration

from rsocket.transports.aioquic_transport import rsocket_serve

CERTIFICATES_PATH_BASE = '../certificates/'
SSL_CERT = 'ssl_cert.pem'
SSL_KEY = 'ssl_key.pem'

class QUICServer():
    def run_server(self, address: str, server_port: int):
        logging.info(SERVING.format(address, server_port))

        configuration = QuicConfiguration(
            is_client=False,
            idle_timeout=600
        )

        # QUIC incorporates TLS in the handshake. So no extra requests!
        configuration.load_cert_chain(CERTIFICATES_PATH_BASE + SSL_CERT, CERTIFICATES_PATH_BASE + SSL_KEY)

        return rsocket_serve(host=address,
                            port=server_port,
                            configuration=configuration,
                            handler_factory=ServerHandler)

