from threading import Thread
from typing import Callable, Tuple
from bleak import BleakClient
import asyncio
import numpy as np

from util.app import App
from util.app_notifier_base import AppNotifierBase

class WitMotionSensor(AppNotifierBase):
    """
    BLE接続されたWitMotionのセンサから値を取得する

    取得した値は、self.current_dataに格納される
    
    専用のスレッドで動くが、BleakClientはasyncioで動かす必要があるようなので
    スレッド内でasyncioのイベントループを作って、そこでBleakClientを動かす
    """
    notify_uuid = "0000ffe4-0000-1000-8000-00805f9a34fb" # 通知を受け取るUUID。恐らく固定値
    write_uuid = "0000ffe9-0000-1000-8000-00805f9a34fb" # 設定を送るためのUUID。

    def __init__(self, 
        mac_address: str,
        app: App,
        on_update: Callable[[Tuple[float,float,float]],None],
        on_terminated: Callable[[Exception],None],
    ) -> None:
        super().__init__(app)
        self.mac_address = mac_address
        self.on_update = on_update
        self.on_terminated = on_terminated

        self.thread = Thread(target=self._run_thread)
        self.finished = False
        self.current_data: Tuple[float,float,float] = (0,0,0)

        self._calibration = False
        self._do_notify = True

    def notify(self):
        self.on_update(self.current_data)

    def start(self, calibration: bool = False, do_notify: bool = True):
        self._calibration = calibration
        self._do_notify = do_notify
        super().start()
        self.thread.start()

    def stop(self):
        self.finished = True

    def _run_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._run_async())

    async def _run_async(self):
        try:
            async with BleakClient(self.mac_address) as client:
                x = client.is_connected
                print("Connected: {0}".format(x))
                if self._calibration:
                    await self._calibrate(client)
                if self._do_notify:
                    await client.start_notify(self.notify_uuid, self._notification_handler)
                    while not self.finished:
                        await asyncio.sleep(0.1)
                    await client.stop_notify(self.notify_uuid)
        except Exception as e:
            self.on_terminated(e)
        finally:
            self.finished = True

    def _notification_handler(self, sender, data: bytearray):
        header_bit = data[0]
        assert header_bit == 0x55
        flag_bit = data[1] # 0x51 or 0x71
        assert flag_bit == 0x61 or flag_bit == 0x71
        # 2 byteずつ取り出して、後ろのbyteが上位ビットになるようにsigned shortに変換
        decoded = [int.from_bytes(data[i:i+2], byteorder='little', signed=True) for i in range(2, len(data), 2)]
        # signed shortの桁数なので、-32768~32767の範囲になる
        # なので一旦正規化してから各単位に合わせる
        ax    = decoded[0] / 32768.0 * 16 * 9.8
        ay    = decoded[1] / 32768.0 * 16 * 9.8
        az    = decoded[2] / 32768.0 * 16 * 9.8
        wx    = decoded[3] / 32768.0 * 2000
        wy    = decoded[4] / 32768.0 * 2000
        wz    = decoded[5] / 32768.0 * 2000
        roll  = decoded[6] / 32768.0 * 180
        pitch = decoded[7] / 32768.0 * 180
        yaw   = decoded[8] / 32768.0 * 180
        # print(f"ax: {ax:.3f}, ay: {ay:.3f}, az: {az:.3f}, wx: {wx:.3f}, wy: {wy:.3f}, wz: {wz:.3f}, roll: {roll:.3f}, pitch: {pitch:.3f}, yaw: {yaw:.3f}")
        self.current_data = (roll * np.pi / 180, pitch * np.pi / 180, yaw * np.pi / 180) # roll, pitch, yawをラジアンに変換して格納
        self.event.set()

    async def _calibrate(self, client: BleakClient):
        # start magnetic calibration
        await client.write_gatt_char(
            self.write_uuid, 
            b'\xFF\xAA\x01\x07\x00')
        for i in range(15, 0, -1):
            print(f"\rCalibration start in {i} seconds...", end="")
            await asyncio.sleep(1)
        await client.write_gatt_char(
            self.write_uuid,
            b'\xFF\xAA\x01\x00\x00')
        print("finish magnetic calibration")
