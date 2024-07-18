from pros.serial.devices.vex.v5_user_device import V5UserDevice
from pros.serial.ports.v5_wireless_port import V5WirelessPort
from pros.serial import decode_bytes_to_str
from pros.cli.common import resolve_v5_port

import asyncio

class VexSerial:
    def __init__(self):
        port, _ = resolve_v5_port(None, 'user')
        ser = V5WirelessPort(port)

        self.device = V5UserDevice(ser)
        self.device.subscribe(b'sout')
        self.device.subscribe(b'serr')

    async def read_packet(self) -> str:
        await asyncio.sleep(0)
        data = self.device.read()
        if not data:
            return ""
        return decode_bytes_to_str(data[1])
        

if __name__ == "__main__":
    pass