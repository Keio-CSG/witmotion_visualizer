from typing import Callable, Optional, Tuple
import open3d as o3d
from scipy.spatial.transform import Rotation

class ImuVisualizer:
    """
    get_data()で取得したIMUのオイラー角を画面に反映する
    """
    def __init__(self) -> None:
        self.local_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1, origin=[0, 0, 0])
        global_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.5, origin=[0, 0, 0])
        self.global_frame = global_frame.sample_points_uniformly(number_of_points=1000)
        # self.rotation_matrix = None

        self.vis = None
        self.on_stop = None
        self.finished = False
        self.get_data: Optional[Callable[[], Tuple[float,float,float]]] = None
        self.prev_data: Optional[Callable[[], Tuple[float,float,float]]] = None

    def start(self, on_stop=None):
        self.on_stop = on_stop
        self.vis = o3d.visualization.VisualizerWithKeyCallback()
        self.vis.create_window()
        self.vis.register_key_callback(256, self.close_window) # ESC
        self.vis.add_geometry(self.local_frame)
        self.vis.add_geometry(self.global_frame)

        while not self.finished:
            if self.get_data is not None and self.prev_data != self.get_data():
                roll, pitch, yaw = self.get_data()
                print(f"roll: {roll}, pitch: {pitch}, yaw: {yaw}")
                R = Rotation.from_euler("zyx", [yaw, pitch, roll]).as_matrix()
                if self.prev_data is not None:
                    inv_prev_R = Rotation.from_euler("xyz", [-self.prev_data[0], -self.prev_data[1], -self.prev_data[2]]).as_matrix()
                    self.local_frame.rotate(inv_prev_R, center=[0, 0, 0])
                self.local_frame.rotate(R, center=(0, 0, 0))
                self.vis.update_geometry(self.local_frame)
                # self.data_for_update = None
                # self.rotation_matrix = R
                self.prev_data = (roll, pitch, yaw)
            self.vis.poll_events()
            self.vis.update_renderer()

    def stop(self):
        self.finished = True
        self.vis.destroy_window()
        if self.on_stop is not None:
            self.on_stop()

    def close_window(self, vis):
        vis.destroy_window()
        self.finished = True
        if self.on_stop:
            self.on_stop()
        return False
    