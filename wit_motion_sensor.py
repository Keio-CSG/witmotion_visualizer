from threading import Thread
from typing import Callable, Tuple
from bleak import BleakClient
import asyncio
import numpy as np

class WitMotionSensor:
    """
    BLE接続されたWitMotionのセンサから値を取得する

    取得した値は、self.current_dataに格納される
    
    専用のスレッドで動くが、BleakClientはasyncioで動かす必要があるようなので
    スレッド内でasyncioのイベントループを作って、そこでBleakClientを動かす
    """
    notify_uuid = "0000ffe4-0000-1000-8000-00805f9a34fb" # 通知を受け取るUUID。恐らく固定値

    def __init__(self, mac_address: str) -> None:
        self.mac_address = mac_address
        self.thread = Thread(target=self.run_thread)
        self.finished = False
        self.current_data: Tuple[float,float,float] = (0,0,0)

    def start(self):
        self.thread.start()

    def finish(self):
        self.finished = True

    def run_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run_async())
        # client = BleakClient(self.mac_address)
        # x = client.is_connected()
        # print("Connected: {0}".format(x))
        # client.start_notify(self.notify_uuid, self.notification_handler)
        # while not self.finished:
        #     time.sleep(0.1)
        # client.stop_notify(self.notify_uuid)
        # client.disconnect()

    async def run_async(self):
        async with BleakClient(self.mac_address) as client:
            x = client.is_connected
            print("Connected: {0}".format(x))
            await client.start_notify(self.notify_uuid, self.notification_handler)
            while not self.finished:
                await asyncio.sleep(0.1)
            await client.stop_notify(self.notify_uuid)

    def notification_handler(self, sender, data: bytearray):
        data_list = [int.from_bytes(data[i:i+1], byteorder='little') for i in range(len(data))]
        ax = (data_list[3] << 8 | data_list[2]) / 32768.0 * 16 * 9.8
        ay = (data_list[5] << 8 | data_list[4]) / 32768.0 * 16 * 9.8
        az = (data_list[7] << 8 | data_list[6]) / 32768.0 * 16 * 9.8
        wx = (data_list[9] << 8 | data_list[8]) / 32768.0 * 2000
        wy = (data_list[11] << 8 | data_list[10]) / 32768.0 * 2000
        wz = (data_list[13] << 8 | data_list[12]) / 32768.0 * 2000
        roll = (data_list[15] << 8 | data_list[14]) / 32768.0 * 180
        pitch = (data_list[17] << 8 | data_list[16]) / 32768.0 * 180
        yaw = (data_list[19] << 8 | data_list[18]) / 32768.0 * 180
        # print(f"ax: {ax:.3f}, ay: {ay:.3f}, az: {az:.3f}, wx: {wx:.3f}, wy: {wy:.3f}, wz: {wz:.3f}, roll: {roll:.3f}, pitch: {pitch:.3f}, yaw: {yaw:.3f}")
        self.current_data = (roll * np.pi / 180, pitch * np.pi / 180, yaw * np.pi / 180) # roll, pitch, yawをラジアンに変換して格納

    # async def run(self, loop):
    #     print("run")
    #     async with BleakClient(self.mac_address, loop=loop) as client:
    #         x = await client.is_connected()
    #         print("Connected: {0}".format(x))
    #         await client.start_notify(self.notify_uuid, self.notification_handler)
    #         await asyncio.sleep(5)
