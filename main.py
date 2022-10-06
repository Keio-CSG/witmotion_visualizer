from typing import Tuple
from imu_visualizer import ImuVisualizer
from util.app import App
from wit_motion_sensor import WitMotionSensor

def main():
    app = App()
    visualizer = ImuVisualizer(app)
    visualizer.start(on_stop=app.stop)

    def on_update(data: Tuple[float,float,float]):
        visualizer.rotation = data
    def on_sensor_terminated(e: Exception):
        print("Sensor terminated:", e)
        visualizer.stop()
    sensor = WitMotionSensor("EA:78:B5:4D:E3:21", app, on_update, on_sensor_terminated)
    sensor.start(calibration=True)

    app.run()
    sensor.stop()


if __name__ == "__main__":
    main()
