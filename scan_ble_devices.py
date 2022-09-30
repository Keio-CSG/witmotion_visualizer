import asyncio
from bleak import BleakScanner

async def run():
    devices = await BleakScanner.discover()
    for d in devices:
        print(f"address: {d.address}, name: {d.name}, uuid: {d.metadata['uuids']}")

loop = asyncio.get_event_loop()
loop.run_until_complete(run())