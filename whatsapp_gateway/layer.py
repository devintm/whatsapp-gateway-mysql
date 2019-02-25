import datetime
import MySQLdb

from config.creds import WHATS_APP_PHONE_NUMBER, MYSQL_USER, MYSQL_PASSWORD

from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_receipts.protocolentities import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_acks.protocolentities import OutgoingAckProtocolEntity
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers import YowLayerEvent
# from yowsup.layers.protocol_messages.protocolentities import Textentity
# from yowsup.layers.protocol_media.protocolentities import ImageDownloadableMediaentity
# from yowsup.layers.protocol_media.protocolentities import LocationMediaentity
# from yowsup.layers.protocol_media.protocolentities import VCardMediaentity


def write_sql_row(sender, receiver, message, message_id, message_type, message_dt):
    """This function writes a row to the messages table in the whatsapp db."""
    try:
        # Create MySQLdb object to connect to the whatsapp database
        con = MySQLdb.connect(host="localhost",
                             user=MYSQL_USER,
                             passwd=MYSQL_PASSWORD,
                             db="whatsapp")
         
        # Create a Cursor object to execute queries with the database open
        cur = con.cursor()

        # Create record in the messages table
        cur.execute("""INSERT INTO messages(sender, receiver, message, message_id, message_type, message_dt) VALUES ("{sender}", "{receiver}", "{message}", "{message_id}", "{message_type}", "{message_dt}")""".format(
            sender=sender, receiver=receiver, message=message,
            message_id=message_id, message_type=message_type,
            message_dt=message_dt))

        con.commit()
        con.close()
        return True

    except MySQLdb.Error as e:
        print("ERROR: Error with database transaction. Time to Rollback.")
        # Rollback the database connection
        con.rollback()
        print "Error {}: {}".format(e.args[0], e.args[1])
        return False

class WhatsAppGatewayLayer(YowInterfaceLayer):
    """This object handles incoming events like onMesssage for new messages."""

    @ProtocolEntityCallback("success")
    def onSuccess(self, entity):
        print("[WhatsAppGatewayLayer] Logged in!")

    @ProtocolEntityCallback("failure")
    def onFailure(self, entity):
        print("[WhatsAppGatewayLayer] Login Failed, reason: {}".format(
            entity.getReason()))

    @ProtocolEntityCallback("message")
    def onMessage(self, entity):

        # TODO convert to print
        print("[WhatsAppGatewayLayer][onMessage] - message received. [type:{}] [ID:{}]".format(
            entity.getType(), entity.getId()
        ))

        if not entity.isGroupMessage():
            if entity.getType() == 'text':
                self.onTextMessage(entity)
            elif entity.getType() == 'media':
                self.onMediaMessage(entity)
            else:  # Unexpected entity type
                pass

        else:  # TODO Group message
            # Not marked as delivered
            pass

    def onTextMessage(self, entity):
        # Get the message body, from phone and message_dt
        message_body = entity.getBody()
        from_phone = entity.getFrom(False)
        message_dt = datetime.datetime.fromtimestamp(
            entity.timestamp)
        print("Received {} from {}".format(message_body, from_phone))

        # Write SQL row for the received text message
        write_sql_row(sender=from_phone, receiver=WHATS_APP_PHONE_NUMBER,
            message=message_body, message_id=entity.getId(),
            message_type='text', message_dt=message_dt.strftime("%Y-%m-%d %H:%i:%s"))

        # process and send a response (read receipt) back to the user
        self.processResponse(entity)

        # ---- Send a message back to the user ----
        # outgoingentity = Textentity(
        #     "Receved!",
        #     to = entity.getFrom())

        # self.toLower(outgoingentity)

    def onMediaMessage(self, entity):
        message_type = entity.getMediaType()

        if message_type == "image":
            image_url = entity.url
            from_phone = entity.getFrom(False)
            message = image_url
            print("Received {} from {}".format(image_url, from_phone))

            # outImage = ImageDownloadableMediaentity(
            #     entity.getMimeType(), entity.fileHash, entity.url, entity.ip,
            #     entity.size, entity.fileName, entity.encoding, entity.width, entity.height,
            #     entity.getCaption(),
            # to = entity.getFrom(), preview =
            # entity.getPreview())

            # self.toLower(outImage)

        elif message_type == "location":

            from_phone = entity.getFrom(False)
            message_coordinates = "({}, {})".format(
                entity.getLatitude(),
                entity.getLongitude())
            message = message_coordinates
            # <message retry="4" from="13001234567@s.whatsapp.net" t="1425016028" offline="4" type="media" id="1425013890-3" notify="Devin Miller">
            # <media latitude="10.629512" type="location" longitude="36.816747" encoding="raw">
            print("Received location {} from {}".format(message_coordinates, from_phone))

            # outLocation = LocationMediaentity(entity.getLatitude(),
            #     entity.getLongitude(), entity.getLocationName(),
            #     entity.getLocationURL(), entity.encoding,
            #     to = entity.getFrom(), preview=entity.getPreview())
            # self.toLower(outLocation)

        elif message_type == "vcard":
            from_phone = entity.getFrom(False)
            message_vcard = "({}, {})".format(
                entity.getName(),
                entity.getCardData())
            message = message_vcard
            print("Received vcard {} from {}".format(message_vcard, from_phone))

            # outVcard = VCardMediaentity(entity.getName(),entity.getCardData(),to = entity.getFrom())
            # self.toLower(outVcard)

        else:  # Unexpected message type
            print("WARNING: Unexpected message type [message_type:{}]".format(
                message_type))
            return

        # Get generic message (entity) details
        message_dt = datetime.datetime.fromtimestamp(
            entity.timestamp)

        # Write SQL row for the received media message
        write_sql_row(sender=from_phone, receiver=WHATS_APP_PHONE_NUMBER,
            message=message, message_id=entity.getId(),
            message_type=message_type, message_dt=message_dt.strftime("%Y-%m-%d %H:%i:%s"))

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        # ack
        ack = OutgoingAckProtocolEntity(
            entity.getId(), "receipt", entity.getType(), entity.getFrom())
        self.toLower(ack)

    @ProtocolEntityCallback("iq")
    def onIq(self, entity):
        print(entity)

    def processResponse(self, entity):
        """Marks the message as delivered and read."""

        # mark as delivered
        receipt = OutgoingReceiptProtocolEntity(
            entity.getId(),
            entity.getFrom())
        self.toLower(receipt)

        # formated_response = "Hello world! This is a response message."

        # mark as read
        receipt = OutgoingReceiptProtocolEntity(
            entity.getId(),
            entity.getFrom(),
            "read")
        self.toLower(receipt)

        # self.toLower(formated_response)
        self.toLower(entity.ack())
        self.toLower(entity.ack(True))

    @ProtocolEntityCallback("event")
    def onEvent(self, layerEvent):

        print("WhatsApp-Plugin : EVENT " + layerEvent.getName())

        if layerEvent.getName() == YowNetworkLayer.EVENT_STATE_DISCONNECTED:
            msg = "WhatsApp-Plugin : Disconnected reason: %s" % layerEvent.getArg(
                "reason")
            print(msg)

            if layerEvent.getArg("reason") == 'Connection Closed':
                # time.sleep(20)
                print("WhatsApp-Plugin : Issueing EVENT_STATE_CONNECT")
                self.getStack().broadcastEvent(
                    YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
            elif layerEvent.getArg("reason") == 'Ping Timeout':
                # time.sleep(20)
                print("WhatsApp-Plugin : Issueing EVENT_STATE_DISCONNECT")
                self.getStack().broadcastEvent(
                    YowLayerEvent(YowNetworkLayer.EVENT_STATE_DISCONNECT))
                # time.sleep(20)
                print("WhatsApp-Plugin : Issueing EVENT_STATE_CONNECT")
                self.getStack().broadcastEvent(
                    YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))

        elif layerEvent.getName() == YowNetworkLayer.EVENT_STATE_CONNECTED:
            print("WhatsApp-Plugin : Connected")
