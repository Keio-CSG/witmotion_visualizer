from typing import Tuple
import open3d as o3d
from scipy.spatial.transform import Rotation
import numpy as np

from util.app import App

class ImuVisualizer:
    """
    get_data()で取得したIMUのオイラー角を画面に反映する
    """
    def __init__(self, app: App) -> None:
        self.app = app
        self.local_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1, origin=[0, 0, 0])
        global_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.5, origin=[0, 0, 0])
        self.global_frame = global_frame.sample_points_uniformly(number_of_points=1000)
        # self.rotation_matrix = None

        self.vis = None
        self.on_stop = None
        self.finished = False
        self.rotation: Tuple[float,float,float] = None
        self.prev_rotation: Tuple[float,float,float] = None

    def start(self, on_stop=None):
        self.on_stop = on_stop
        self.vis = o3d.visualization.VisualizerWithKeyCallback()
        self.vis.create_window()
        self.vis.register_key_callback(256, self._close_window) # ESC
        self.vis.add_geometry(self.local_frame)
        self.vis.add_geometry(self.global_frame)

        self.app.add_event(self._render)

    def _render(self):
        if self.rotation is not None:
            roll, pitch, yaw = self.rotation
            print(f"roll: {roll*180/np.pi:.2f} deg, pitch: {pitch*180/np.pi:.2f} deg, yaw: {yaw*180/np.pi:.2f} deg")
            R = Rotation.from_euler("ZYX", [yaw, pitch, roll]).as_matrix()
            if self.prev_rotation is not None:
                inv_prev_R = Rotation.from_euler("XYZ", [-self.prev_rotation[0], -self.prev_rotation[1], -self.prev_rotation[2]]).as_matrix()
                self.local_frame.rotate(inv_prev_R, center=(0, 0, 0))
            self.local_frame.rotate(R, center=(0, 0, 0))
            self.vis.update_geometry(self.local_frame)
            self.prev_rotation = self.rotation
            self.rotation = None
        self.vis.poll_events()
        self.vis.update_renderer()
        if not self.finished:
            self.app.add_event(self._render)

    def stop(self):
        self.finished = True
        self.vis.destroy_window()
        if self.on_stop is not None:
            self.on_stop()

    def _close_window(self, vis):
        self.stop()
        return False
    