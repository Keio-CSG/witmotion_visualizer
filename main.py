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
    sensor = WitMotionSensor("EA:78:B5:4D:E3:21", app, on_update)
    sensor.start(calibration=True)

    app.run()
    sensor.stop()


if __name__ == "__main__":
    main()
