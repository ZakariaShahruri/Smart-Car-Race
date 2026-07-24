import os
import socketserver
import tempfile
import threading

from car_control import normalize_command, send_command


def test_normalize_command_defaults_to_stop_with_no_args():
    assert normalize_command(["car_control.py"]) == "stop"


def test_normalize_command_lowercases_and_strips():
    assert normalize_command(["car_control.py", "  FORWARD  "]) == "forward"


def test_send_command_round_trips_over_unix_socket():
    # AF_UNIX paths are capped at ~104 chars on macOS/BSD, so this uses a short
    # path directly under /tmp rather than pytest's (much deeper) tmp_path fixture.
    fd, sock_path = tempfile.mkstemp(prefix="car-", suffix=".sock")
    os.close(fd)
    os.remove(sock_path)

    class EchoHandler(socketserver.BaseRequestHandler):
        def handle(self):
            data = self.request.recv(64)
            self.request.sendall(b"ok:" + data)

    server = socketserver.UnixStreamServer(sock_path, EchoHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        reply = send_command("forward", sock_path=sock_path)
    finally:
        server.shutdown()
        server.server_close()
        if os.path.exists(sock_path):
            os.remove(sock_path)

    assert reply == "ok:forward"
