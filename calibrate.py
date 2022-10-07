"""
キャリブレーションだけする
"""

from util.app import App
from wit_motion_sensor import WitMotionSensor

def main():
    app = App()
    sensor = WitMotionSensor("EA:78:B5:4D:E3:21", app, lambda _: None, lambda _: None)
    sensor.start(calibration=True, do_notify=False)
    sensor.stop()


if __name__ == "__main__":
    main()
