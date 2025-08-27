#--*--coding:utf-8--*--
import struct, logging

class GandanMsg:
    def __init__(self, pubsub, topic, data):
        if pubsub == 'PUB' or pubsub == 'P':
            self.pubsub = 'P'
        elif pubsub == 'SUB' or pubsub == 'S':
            self.pubsub = 'S'
        else:
            raise Exception('pubsub')
        self.topic_size = len(bytes(topic, "utf-8"))
        self.data_size = len(bytes(data,"utf-8"))
        (self.topic, self.data) = (topic, data)
        self.total_size = 0
        self.total_size = len(bytes(self))
        self.protocol_type = "tcp"

    def __bytes__(self):
        _b = bytes(self.pubsub, "utf-8")
        _b += struct.pack("!i", self.total_size)
        _b += struct.pack("!i", self.topic_size)
        _b += bytes(self.topic, "utf-8")
        _b += bytes(self.data, "utf-8")
        return _b
    
    def __str__(self):
        return self.topic+":"+self.data

    @staticmethod
    async def recv_async(reader):
        """
        비동기 버전: reader는 asyncio.StreamReader 등 비동기 reader 객체여야 하며, read(n) 메서드를 비동기적으로 호출해야 합니다.
        """
        pubsub_byte = await reader.read(65535)
        if len(pubsub_byte) == 0:
            raise Exception("conn")

        try:
            total_size_byte = pubsub_byte[1:5]
 
            total_size = struct.unpack("!i", total_size_byte)[0]
            total_byte = pubsub_byte[5:total_size+5]
            topic_size = struct.unpack("!i", total_byte[0:4])[0]
            topic_bytes = total_byte[4:4+topic_size]
            topic = str(topic_bytes, "utf-8")
            data_bytes = total_byte[4+topic_size:]
            data = str(data_bytes, "utf-8")
        except Exception as e:
            raise Exception('convert total_size')
        logging.info("recv pubsub: %s, topic: %s, data: %s" % (pubsub_byte[0:1], topic, data))
        return GandanMsg(str(pubsub_byte[0:1], "utf-8"), topic, data)

    @staticmethod
    def recv_sync(sock):
        """
        동기 버전: reader는 socket 등 file-like 객체여야 하며, read(n) 메서드를 동기적으로 호출해야 합니다.
        """
        pubsub_byte = sock.recv(65535)
        if len(pubsub_byte) == 0:
            raise Exception("timed out")

        try:
            total_size_byte = pubsub_byte[1:5]
 
            total_size = struct.unpack("!i", total_size_byte)[0]
            total_byte = pubsub_byte[5:total_size+5]
            topic_size = struct.unpack("!i", total_byte[0:4])[0]
            topic_bytes = total_byte[4:4+topic_size]
            topic = str(topic_bytes, "utf-8")
            data_bytes = total_byte[4+topic_size:]
            data = str(data_bytes, "utf-8")
        except Exception as e:
            raise Exception('convert total_size')
        logging.info("recv pubsub: %s, topic: %s, data: %s" % (pubsub_byte[0:1], topic, data))
        return GandanMsg(str(pubsub_byte[0:1], "utf-8"), topic, data)