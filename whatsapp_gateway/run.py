import os
import sys
import logging
import traceback

from config.creds import CREDENTIALS


def setup_logger():
    # TODO integrate into it's own log file
    logging.getLogger("yowsup.stacks.yowstack").addHandler(
        logging.NullHandler())
    logging.basicConfig(level=logging.INFO)


def initialize_whatsapp_gateway():
    # Setup the yowsup stack
    stack = WhatsAppGatewayStack(
        credentials=CREDENTIALS,
        encryptionEnabled=True
    )
    # Start listening for signals - i.e. incoming messages...
    try:
        # Sometimes this stack.start loop stops, so I placed it in a While True loop
        stack.start()
    except Exception as e:
        print('FAILURE: {0} : {1}'.format(e, traceback.format_exc()))


from stack import WhatsAppGatewayStack

# Setup the logger - to get more logs!
setup_logger()

# Load whats app gateway
initialize_whatsapp_gateway()
