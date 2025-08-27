#--*--coding=utf-8--*--
import sys, re, logging, traceback, asyncio
from os import path
import re, threading
import hashlib, base64, json
import ssl
import websockets

try:
    from .GandanMsg import *
    from .MMAP  import *
except Exception as e:
    from gandan.GandanMsg import *
    from gandan.MMAP  import *

class Gandan:
    def __init__(self, ip_port, debug=False):
        self.ip_port = ip_port

        self.sub_topic = {}
        self.sub_ws_topic = {}
        self.sub_topic_lock = asyncio.Lock()

    @staticmethod
    def setup_log(path, level = logging.DEBUG):
        l_format = '%(asctime)s:%(msecs)03d^%(levelname)s^%(funcName)20s^%(lineno)04d^%(message)s'
        d_format = '%Y-%m-%d^%H:%M:%S'
        logging.basicConfig(filename=path, format=l_format, datefmt=d_format,level=level)

    @staticmethod
    def error_stack(stdout = False):
        _type, _value, _traceback = sys.exc_info()
        logging.info("#Error" + str(_type) + str(_value))
        for _err_str in traceback.format_tb(_traceback):
            if stdout == False:
                logging.info(_err_str)
            else:
                logging.info(_err_str)
                
    @staticmethod
    def version():
        return int(re.sub('\.','',sys.version.split(' ')[0][0]))

    async def ws_handler(self, websocket):
        path = websocket.request.path
        key_value = path.split("?")[1]
        (key, value) = key_value.split("=")

        if key != "topic":
            raise Exception("Invalid request path")

        # we don't receive message from websocket
        topic = value
        if topic in self.sub_ws_topic:
            if not websocket in self.sub_ws_topic[topic]:
                self.sub_ws_topic[topic].append(websocket)
        else:
            self.sub_ws_topic[topic] = [websocket]

    async def tcp_handler(self, reader, writer):
        addr = writer.get_extra_info('peername')
        logging.info("addr : %s" % str(addr))
        while(True):
            try:
                msg = await GandanMsg.recv_async(reader)
                if msg == None:
                    continue
                logging.info("data : %s" % str(msg))

                if msg.pubsub == 'P':
                    try:
                        async with self.sub_topic_lock:
                            remove_writers, remove_ws_writers = [], []
                            if msg.topic in self.sub_topic:
                                for sub_writer in self.sub_topic[msg.topic]:
                                    try:
                                        sub_writer.write(bytes(msg))
                                        await sub_writer.drain()
                                    except Exception as e:
                                        logging.info(f"writer error: {e}")
                                        remove_writers.append(sub_writer)

                            if msg.topic in self.sub_ws_topic:
                                for ws in self.sub_ws_topic[msg.topic]:
                                    try:
                                        await ws.send(bytes(msg.data, "utf-8"))
                                    except Exception as e:
                                        logging.info(f"writer error: {str(e)}")
                                        remove_ws_writers.append(ws)

                            # 에러난 writer 제거
                            for w in remove_writers:
                                if w in self.sub_topic[msg.topic]:
                                    self.sub_topic[msg.topic].remove(w)

                            # 에러난 writer 제거
                            for w in remove_ws_writers:
                                if w in self.sub_ws_topic[msg.topic]:
                                    self.sub_ws_topic[msg.topic].remove(w)
                    except Exception as e:
                        logging.info(f"lock or pub error: {e}")
                elif msg.pubsub == 'S':
                    try:
                        logging.info("sub topic: %s" % msg.topic)
                        async with self.sub_topic_lock:
                            if msg.topic not in self.sub_topic:
                                self.sub_topic[msg.topic] = [writer]
                            else:
                                if writer not in self.sub_topic[msg.topic]:
                                    self.sub_topic[msg.topic].append(writer)
                    except Exception as e:
                        logging.info(f"lock or sub error: {e}")
            except Exception as e:
                logging.info("error : %s" % str(e))
                break

    # start를 asyncio 기반으로 변경
    async def start(self, certfile="cert.pem", keyfile = "key.pem"):
        async def client_connected_cb(reader, writer):
            await self.tcp_handler(reader, writer)

        async def client_connected_cb_ws(websocket):
            await self.ws_handler(websocket)
            try:
                async for message in websocket:
                    logging.info(f"클라이언트 메시지 수신: {message}")
            except Exception as e:
                logging.info(f"WebSocket 에러: {e}")
                pass

        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_ctx.load_cert_chain(certfile=certfile, keyfile=keyfile)

        tcp_server = await asyncio.start_server(
            client_connected_cb,
            self.ip_port[0], self.ip_port[1]
        )
        ws_server = await websockets.serve(
            client_connected_cb_ws, 
            self.ip_port[2], 
            self.ip_port[3], ssl = ssl_ctx
        )
        async with tcp_server, ws_server:
            logging.info("------------ MW Gandan Version[%d] Start --------------" % Gandan.version())
            tcp_task = asyncio.create_task(tcp_server.serve_forever())
            ws_task = asyncio.create_task(ws_server.serve_forever())
            try:
                await asyncio.gather(tcp_task, ws_task)
                #await ws_server.serve_forever()
            except Exception as e:
                logging.info(str(e))
            finally:
                tcp_task.cancel()
                ws_task.cancel()
                pass

if __name__ == "__main__":
    try:
        l_ip_port = ("0.0.0.0", 59500, "0.0.0.0", 59501)
        mw = Gandan(l_ip_port)
        Gandan.setup_log(datetime.datetime.now().strftime("/tmp/%Y%m%d")+".Gandan.log")
        asyncio.run(mw.start())
    except Exception as e:
        logging.error("Error in Gandan", e)