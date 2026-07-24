#!/usr/bin/env python3
import os
import socket
import sys

SOCK_PATH = "/var/run/car.sock"


def normalize_command(argv: list[str]) -> str:
    return argv[1].strip().lower() if len(argv) > 1 else "stop"


def send_command(command: str, sock_path: str = SOCK_PATH) -> str:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(sock_path)
        s.sendall(command.encode())
        return s.recv(64).decode().strip()


def main() -> None:
    os.chdir("/tmp")
    command = normalize_command(sys.argv)
    try:
        print(send_command(command))
    except FileNotFoundError:
        print("ERROR: car_daemon is not running", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # noqa: BLE001 - last-resort CLI error report, any failure should print and exit 1
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
