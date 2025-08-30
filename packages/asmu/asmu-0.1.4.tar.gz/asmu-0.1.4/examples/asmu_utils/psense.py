"""psense.py"""
from typing import List, Optional

import serial


class PSense():
    def __init__(self, port: str, baud: int):
        self.port = port
        self.baud = baud
        self.serial: Optional[serial.Serial] = None

    def __enter__(self) -> "PSense":
        try:
            self.serial = serial.Serial(self.port, self.baud, timeout=1)
        except serial.SerialException:
            print(f"PSense - could not open port {self.port}")
        return self

    def read_line(self) -> Optional[List[float]]:
        if self.serial is None:
            raise serial.SerialException("No connection opened openend.")

        # clear buffer
        self.serial.reset_input_buffer()

        # block until read one line
        line = b""
        while not line:
            line = self.serial.readline()

        # parse recieved line
        str_line = line.decode("utf-8").strip()
        try:
            list = [float(s) for s in str_line.split(" ")]
        except ValueError:
            return None
        if len(list) == 16:
            return list
        else:
            return None

    def __exit__(self, *args) -> None:  # type: ignore[no-untyped-def]
        if self.serial is not None:
            self.serial.close()
