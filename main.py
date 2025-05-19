from object_3d import *
from camera import *
from projection import *
import pygame as pg
import os
import math
import sys



class SoftwareRender:
    def __init__(self):
        pg.init()
        self.RES = self.WIDTH, self.HEIGHT = 1600, 900
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT // 2
        self.FPS = 60
        self.screen = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont('Arial', 20)
        self.model_list_width = 300
        self.model_list_rect = pg.Rect(0, 0, self.model_list_width, self.HEIGHT)

        # 🧠 Corrected location and structure
        self.resources_path = self.get_base_path('resources')
        if not os.path.exists(self.resources_path):
            os.makedirs(self.resources_path)
            print("Created 'resources/' folder. Please place your .obj model files there.")

        self.model_files = [f for f in os.listdir(self.resources_path) if f.endswith('.obj')]
        if not self.model_files:
            print("No .obj files found in 'resources/'. Exiting.")
            sys.exit()

        self.selected_index = 0
        self.object = None
        self.create_objects()

    def get_base_path(self, *paths):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, *paths)




    def create_objects(self):
        self.camera = Camera(self, [-5, 6, -55])
        self.projection = Projection(self)
        self.load_model(self.model_files[self.selected_index])

    def load_model(self, filename):
        self.object = self.get_object_from_file(os.path.join(self.resources_path, filename))
        self.object.rotate_y(-math.pi / 4)
        self.current_model_name = filename
        self.vertex_count = len(self.object.vertices)
        self.face_count = len(self.object.faces)

    def get_object_from_file(self, filepath):
        vertex, faces = [], []
        with open(filepath) as f:
            for line in f:
                if line.startswith('v '):
                    vertex.append([float(i) for i in line.split()[1:]] + [1])
                elif line.startswith('f'):
                    faces_ = line.split()[1:]
                    faces.append([int(face_.split('/')[0]) - 1 for face_ in faces_])
        return Object3D(self, vertex, faces)

    def draw_sidebar(self):
        pg.draw.rect(self.screen, pg.Color('gray25'), self.model_list_rect)
        for i, filename in enumerate(self.model_files):
            color = pg.Color('orange') if i == self.selected_index else pg.Color('white')
            text_surface = self.font.render(filename, True, color)
            self.screen.blit(text_surface, (10, 10 + i * 25))

        stats = [
            f"Model: {self.current_model_name}",
            f"Vertices: {self.vertex_count}",
            f"Polygons: {self.face_count}",
        ]
        for i, stat in enumerate(stats):
            text_surface = self.font.render(stat, True, pg.Color('lightblue'))
            self.screen.blit(text_surface, (10, 600 + i * 25))

    def draw(self):
        self.screen.fill(pg.Color('darkslategray'))
        self.object.draw()
        self.draw_sidebar()

    def handle_mouse_click(self, pos):
        x, y = pos
        if x < self.model_list_width:
            index = y // 25
            if 0 <= index < len(self.model_files):
                self.selected_index = index
                self.load_model(self.model_files[index])

    def run(self):
        while True:
            self.draw()
            self.camera.control()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos)

            pg.display.set_caption(f'{self.current_model_name} | FPS: {self.clock.get_fps():.2f}')
            pg.display.flip()
            self.clock.tick(self.FPS)


if __name__ == '__main__':
    try:
        app = SoftwareRender()
        app.run()
    except Exception as e:
        import traceback
        with open("crash_log.txt", "w") as f:
            f.write("The application has crashed:\n")
            traceback.print_exc(file=f)
        print("An error occurred. See crash_log.txt for details.")