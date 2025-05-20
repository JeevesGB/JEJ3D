import pygame as pg
from matrix_functions import *

class Camera:
    def __init__(self, render, position):
        self.render = render
        self.position = np.array([*position, 1.0])
        self.forward = np.array([0, 0, 1, 1])
        self.up = np.array([0, 1, 0, 1])
        self.right = np.array([1, 0, 0, 1])
        self.h_fov = math.pi / 3
        self.v_fov = self.h_fov * (render.HEIGHT / render.WIDTH)
        self.near_plane = 0.1
        self.far_plane = 100
        self.moving_speed = 0.2
        self.rotation_speed = 0.01
        self.distance = 10.0  # Initial distance from the model centroid
        self.anglePitch = 0
        self.angleYaw = 0
        self.angleRoll = 0
        self.target = np.array([0, 0, 0, 1])  # Initial target (centroid), updated later

    def set_target(self, vertices):
        # Calculate the centroid of the model's vertices
        if vertices:
            centroid = np.mean(vertices, axis=0)
            self.target = np.array([centroid[0], centroid[1], centroid[2], 1.0])
        else:
            self.target = np.array([0, 0, 0, 1])  # Default to origin if no vertices

    def control(self):
        key = pg.key.get_pressed()
        # Rotate around the target using arrow keys
        if key[pg.K_LEFT]:
            self.camera_yaw(-self.rotation_speed)
        if key[pg.K_RIGHT]:
            self.camera_yaw(self.rotation_speed)
        if key[pg.K_UP]:
            self.camera_pitch(-self.rotation_speed)
        if key[pg.K_DOWN]:
            self.camera_pitch(self.rotation_speed)
        # Zoom in/out with W/S (adjust distance)
        if key[pg.K_w]:
            self.distance = max(2.0, self.distance - self.moving_speed)  # Minimum distance
        if key[pg.K_s]:
            self.distance += self.moving_speed

        # Update camera position to orbit around the target
        self.update_position()


    def camera_yaw(self, angle):
        self.angleYaw += angle

    def camera_pitch(self, angle):
        self.anglePitch = max(-math.pi / 2 + 0.1, min(math.pi / 2 - 0.1, self.anglePitch + angle))  # Limit pitch

    def axiiIdentity(self):
        self.forward = np.array([0, 0, 1, 1])
        self.up = np.array([0, 1, 0, 1])
        self.right = np.array([1, 0, 0, 1])

    def update_position(self):
        # Calculate new position based on yaw, pitch, and distance from target
        yaw = self.angleYaw
        pitch = self.anglePitch
        # Convert spherical coordinates to Cartesian
        x = self.distance * math.cos(pitch) * math.sin(yaw)
        y = self.distance * math.sin(pitch)
        z = self.distance * math.cos(pitch) * math.cos(yaw)
        self.position = self.target + np.array([x, y, z, 0])  # Add offset to target

        # Update forward vector to point toward the target
        direction = self.target - self.position
        self.forward = direction / np.linalg.norm(direction[:3])  # Normalize direction
        self.forward = np.append(self.forward[:3], [1])  # Ensure homogeneous coordinate

    def camera_update_axii(self):
        # Compute right and up vectors based on forward and world up
        world_up = np.array([0, 1, 0])
        self.right = np.cross(world_up, self.forward[:3])
        if np.linalg.norm(self.right) < 0.01:  # Handle near-vertical forward
            self.right = np.cross(np.array([1, 0, 0]), self.forward[:3])
        self.right = np.append(self.right / np.linalg.norm(self.right), [0])
        self.up = np.cross(self.forward[:3], self.right[:3])
        self.up = np.append(self.up / np.linalg.norm(self.up), [0])

    def camera_matrix(self):
        self.camera_update_axii()
        return self.translate_matrix() @ self.rotate_matrix()

    def translate_matrix(self):
        x, y, z, w = self.position
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [-x, -y, -z, 1]
        ])

    def rotate_matrix(self):
        rx, ry, rz, w = self.right
        fx, fy, fz, w = self.forward
        ux, uy, uz, w = self.up
        return np.array([
            [rx, ux, fx, 0],
            [ry, uy, fy, 0],
            [rz, uz, fz, 0],
            [0, 0, 0, 1]
        ])