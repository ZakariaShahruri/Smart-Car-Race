#!/usr/bin/env python3
"""
car_daemon.py  —  persistent GPIO motor controller
Socket: /var/run/car.sock
Command format: "command" or "command/speed" (speed 0-100)
Commands: forward, backward, left, right,
          forward-left, forward-right, backward-left, backward-right,
          spin-left, spin-right, stop
"""

import os
import socket

os.environ["GPIOZERO_PIN_FACTORY"] = "lgpio"
os.environ["HOME"] = "/tmp"
os.chdir("/tmp")

from gpiozero import DigitalOutputDevice

SOCK_PATH = "/var/run/car.sock"

IN1 = DigitalOutputDevice(5)   # left backward
IN2 = DigitalOutputDevice(6)   # left forward
IN3 = DigitalOutputDevice(13)  # right backward
IN4 = DigitalOutputDevice(19)  # right forward

def motors(lf, lb, rf, rb):
    IN2.value = lf
    IN1.value = lb
    IN4.value = rf
    IN3.value = rb

def forward():      motors(1, 0, 1, 0)
def backward():     motors(0, 1, 0, 1)
def left():         motors(0, 0, 1, 0)   # arc left:  right motor only
def right():        motors(1, 0, 0, 0)   # arc right: left motor only
def forward_left(): motors(0, 0, 1, 0)
def forward_right():motors(1, 0, 0, 0)
def backward_left():motors(0, 0, 0, 1)
def backward_right():motors(0, 1, 0, 0)
def spin_left():    motors(0, 1, 1, 0)   # left bwd, right fwd
def spin_right():   motors(1, 0, 0, 1)   # left fwd, right bwd
def stop():         motors(0, 0, 0, 0)

COMMANDS = {
    "forward":        forward,
    "backward":       backward,
    "left":           left,
    "right":          right,
    "forward-left":   forward_left,
    "forward-right":  forward_right,
    "backward-left":  backward_left,
    "backward-right": backward_right,
    "spin-left":      spin_left,
    "spin-right":     spin_right,
    "stop":           stop,
}

if os.path.exists(SOCK_PATH):
    os.remove(SOCK_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCK_PATH)
os.chmod(SOCK_PATH, 0o777)
server.listen(5)

print(f"car_daemon listening on {SOCK_PATH}", flush=True)
stop()

try:
    while True:
        conn, _ = server.accept()
        with conn:
            data = conn.recv(64).decode().strip().lower()
            parts = data.split("/")
            cmd = parts[0]
            fn = COMMANDS.get(cmd, stop)
            fn()
            conn.sendall(b"ok\n")
            print(f"cmd: {cmd}", flush=True)
except KeyboardInterrupt:
    pass
finally:
    stop()
    server.close()
    if os.path.exists(SOCK_PATH):
        os.remove(SOCK_PATH)
