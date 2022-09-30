import asyncio
from typing import Tuple
from imu_visualizer import ImuVisualizer
from wit_motion_sensor import WitMotionSensor

def main():
    visualizer = ImuVisualizer()

    sensor = WitMotionSensor("EA:78:B5:4D:E3:21")
    sensor.start()

    def get_data():
        # print(f"current data: {sensor.current_data}")
        return sensor.current_data

    visualizer.get_data = get_data

    visualizer.start(on_stop=sensor.finish)


if __name__ == "__main__":
    main()
