#!/usr/bin/env python3
import os
import socket
import sys

os.chdir("/tmp")

SOCK_PATH = "/var/run/car.sock"

command = sys.argv[1].strip().lower() if len(sys.argv) > 1 else "stop"

try:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(SOCK_PATH)
        s.sendall(command.encode())
        reply = s.recv(64).decode().strip()
        print(reply)
except FileNotFoundError:
    print("ERROR: car_daemon is not running", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
