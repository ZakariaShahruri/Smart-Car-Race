#!/usr/bin/env python3
"""
car_daemon.py  —  persistent GPIO motor controller
Socket: /var/run/car.sock
Command format: "command" or "command/speed" (speed 0-100)
Commands: forward, backward, left, right,
          forward-left, forward-right, backward-left, backward-right,
          spin-left, spin-right, stop
"""

import logging
import os
import socket

SOCK_PATH = "/var/run/car.sock"
logger = logging.getLogger(__name__)

# (left-forward, left-backward, right-forward, right-backward) pin states per command.
COMMANDS: dict[str, tuple[int, int, int, int]] = {
    "forward":        (1, 0, 1, 0),
    "backward":       (0, 1, 0, 1),
    "left":           (0, 0, 1, 0),  # arc left:  right motor only
    "right":          (1, 0, 0, 0),  # arc right: left motor only
    "forward-left":   (0, 0, 1, 0),
    "forward-right":  (1, 0, 0, 0),
    "backward-left":  (0, 0, 0, 1),
    "backward-right": (0, 1, 0, 0),
    "spin-left":      (0, 1, 1, 0),  # left bwd, right fwd
    "spin-right":     (1, 0, 0, 1),  # left fwd, right bwd
    "stop":           (0, 0, 0, 0),
}


def resolve(command: str) -> tuple[int, int, int, int]:
    """Look up the pin state for a raw socket command, defaulting to stop."""
    return COMMANDS.get(command, COMMANDS["stop"])


class MotorController:
    """Owns the GPIO pins for the lifetime of the daemon."""

    def __init__(self) -> None:
        os.environ["GPIOZERO_PIN_FACTORY"] = "lgpio"
        os.environ["HOME"] = "/tmp"
        os.chdir("/tmp")

        from gpiozero import DigitalOutputDevice

        self._in1 = DigitalOutputDevice(5)   # left backward
        self._in2 = DigitalOutputDevice(6)   # left forward
        self._in3 = DigitalOutputDevice(13)  # right backward
        self._in4 = DigitalOutputDevice(19)  # right forward

    def apply(self, lf: int, lb: int, rf: int, rb: int) -> None:
        self._in2.value = lf
        self._in1.value = lb
        self._in4.value = rf
        self._in3.value = rb

    def run(self, command: str) -> None:
        self.apply(*resolve(command))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    controller = MotorController()

    if os.path.exists(SOCK_PATH):
        os.remove(SOCK_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCK_PATH)
    os.chmod(SOCK_PATH, 0o777)
    server.listen(5)

    logger.info("car_daemon listening on %s", SOCK_PATH)
    controller.run("stop")

    try:
        while True:
            conn, _ = server.accept()
            with conn:
                data = conn.recv(64).decode().strip().lower()
                command = data.split("/")[0]
                controller.run(command)
                conn.sendall(b"ok\n")
                logger.info("cmd: %s", command)
    except KeyboardInterrupt:
        pass
    finally:
        controller.run("stop")
        server.close()
        if os.path.exists(SOCK_PATH):
            os.remove(SOCK_PATH)


if __name__ == "__main__":
    main()
