import socketserver
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from time import sleep

import cv2
import depthai as dai

HTTP_SERVER_PORT = 8090


class TCPServerRequest(socketserver.BaseRequestHandler):
    def handle(self):
        header = 'HTTP/1.0 200 OK\r\nServer: Mozarella/2.2\r\nAccept-Range: bytes\r\nConnection: close\r\nMax-Age: 0\r\nExpires: 0\r\nCache-Control: no-cache, private\r\nPragma: no-cache\r\nContent-Type: application/json\r\n\r\n'
        self.request.send(header.encode())
        while True:
            sleep(0.1)
            if hasattr(self.server, 'datatosend'):
                self.request.send(self.server.datatosend.encode() + "\r\n".encode())


class VideoStreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            while True:
                sleep(0.1)
                if hasattr(self.server, 'frametosend'):
                    ok, encoded = cv2.imencode('.jpg', self.server.frametosend)
                    self.wfile.write("--jpgboundary".encode())
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', str(len(encoded)))
                    self.end_headers()
                    self.wfile.write(encoded)
                    self.end_headers()
        except BrokenPipeError:
            print("Broken pipe, closing connection...")


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass


def get_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def main():
    print("Running Hivebox Live...")

    server_HTTP = ThreadedHTTPServer(('0.0.0.0', HTTP_SERVER_PORT), VideoStreamHandler)
    th2 = threading.Thread(target=server_HTTP.serve_forever)
    th2.daemon = True
    th2.start()

    def create_pipeline():
        pipeline = dai.Pipeline()
        cam = pipeline.create(dai.node.ColorCamera)
        cam.setPreviewSize(300, 300)
        cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        cam.setInterleaved(False)

        xoutRgb = pipeline.create(dai.node.XLinkOut)
        xoutRgb.setStreamName("rgb")
        cam.preview.link(xoutRgb.input)
        return pipeline

    # Pipeline is defined, now we can connect to the device
    with dai.Device(create_pipeline()) as device:
        print("DepthAI is up & running.")
        print(f"Navigate to 'http://{get_ip()}:{str(HTTP_SERVER_PORT)}' with Chrome to see the mjpeg stream")

        previewQueue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        while True:
            server_HTTP.frametosend = previewQueue.get().getCvFrame()

if __name__ == '__main__':
    main()
