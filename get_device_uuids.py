"""
特定のMACアドレスのBLEデバイスのServiceとCharacteristicを表示する
"""

import asyncio
from bleak import BleakClient

address = "EA:78:B5:4D:E3:21" # scan_ble_devices.pyで取得したMACアドレスを指定

async def run(address, loop):
    async with BleakClient(address, loop=loop) as client:
        x = await client.is_connected()
        print("Connected: {0}".format(x))
        for service in client.services:
            print(f"{service.uuid}: {service.description}: {[f'{c.properties},{c.uuid}' for c in service.characteristics]}")

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address, loop))
