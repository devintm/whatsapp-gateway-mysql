import sys
from layer import WhatsAppGatewayLayer

from yowsup.stacks import YowStackBuilder
from yowsup.layers.auth import AuthError
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers import YowLayerEvent


class WhatsAppGatewayStack(object):
    """This is the basic stack object which will read the credentials and handle
    encryption."""

    def __init__(self, credentials, encryptionEnabled=True):
        stackBuilder = YowStackBuilder()

        self.stack = stackBuilder\
            .pushDefaultLayers(encryptionEnabled)\
            .push(WhatsAppGatewayLayer)\
            .build()

        # Set the credentials set in the config/creds.py
        self.stack.setCredentials(credentials)

    def start(self):
        # Broadcase the connect event
        self.stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))

        try:
            # Poll for messages every 500ms (0.5 seconds)
            self.stack.loop(timeout=0.5, discrete=0.5)
        except AuthError as e:
            # Log authentication error
            print("Auth Error, reason %s" % e)
        except KeyboardInterrupt:
            # Log that the user closed the app
            print("\nYowsdown")
            sys.exit(0)
