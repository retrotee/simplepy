import tkinter as tk
import time
import math
import random
from tkinter import PhotoImage
from PIL import Image, ImageTk


class SimplePy:
    def __init__(self, title="SimplePy Game", width=800, height=600, fps=60):
        self.root = tk.Tk()
        self.root.title(title)
        self.width = width
        self.height = height
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=width, height=height, bg="white")
        self.canvas.pack()

        self.running = False
        self.fps = fps
        self.frame_time = 1.0 / fps
        self.sprites = []
        self.keys_pressed = set()
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_pressed = False
        self.is_frozen = False
        self.target_fps = fps
        self.current_fps = 0
        self.max_frame_skip = 5
        self.pen_lines = []
        self.fps_limit = 60

        self.root.bind("<KeyPress>", self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)
        self.root.bind("<Motion>", self._on_mouse_move)
        self.root.bind("<Button-1>", self._on_mouse_press)
        self.root.bind("<ButtonRelease-1>", self._on_mouse_release)

        self.on_start = None
        self.on_update = None
        self.on_draw = None

        self.last_frame_time = time.time()
        self.frame_count = 0

    def _on_key_press(self, event):
        self.keys_pressed.add(event.keysym.lower())

    def _on_key_release(self, event):
        if event.keysym.lower() in self.keys_pressed:
            self.keys_pressed.remove(event.keysym.lower())

    def _on_mouse_move(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y

    def _on_mouse_press(self, event):
        self.mouse_pressed = True
        self.mouse_x = event.x
        self.mouse_y = event.y

    def _on_mouse_release(self, event):
        self.mouse_pressed = False

    def run(self):
        self.running = True

        if self.on_start:
            self.on_start()

        self._game_loop()
        self.root.mainloop()

    def _game_loop(self):
        if not self.running:
            return

        frame_start_time = time.time()
        loops = 0
        while time.time() - frame_start_time < self.frame_time and loops < self.max_frame_skip:
            if self.on_update and not self.is_frozen:
                self.on_update()

            if not self.is_frozen:
                for sprite in self.sprites:
                    sprite.update()

                    if (sprite.x < self.mouse_x < sprite.x + sprite.width and
                            sprite.y < self.mouse_y < sprite.y + sprite.height):
                        if sprite.on_hover:
                            sprite.on_hover()
            loops += 1

        self.canvas.delete("all")

        for line in self.pen_lines:
            self.canvas.create_line(
                line["x1"], line["y1"],
                line["x2"], line["y2"],
                fill=line["color"],
                width=line["width"]
            )

        self.sprites.sort(key=lambda sprite: sprite.layer)

        for sprite in self.sprites:
            sprite.draw(self.canvas)

        if self.on_draw:
            self.on_draw()

        elapsed_time = time.time() - frame_start_time
        sleep_time = max(0, self.frame_time - elapsed_time)
        if self.fps_limit > 0:
            sleep_time = min(sleep_time, 1.0 / self.fps_limit)

        self.root.after(int(sleep_time * 1000), self._game_loop)

        self.frame_count += 1
        current_time = time.time()
        time_diff = current_time - self.last_frame_time

        if time_diff >= 1.0:
            self.current_fps = self.frame_count
            self.frame_count = 0
            self.last_frame_time = current_time

    def is_key_pressed(self, key):
        return key.lower() in self.keys_pressed

    def quit(self):
        self.running = False
        self.root.destroy()

    def create_sprite(self, image_path=None, x=0, y=0, width=50, height=50, color="blue"):
        sprite = Sprite(self, image_path, x, y, width, height, color)
        self.sprites.append(sprite)
        return sprite

    def check_collision(self, sprite1, sprite2):
        return (sprite1.x < sprite2.x + sprite2.width and
                sprite1.x + sprite1.width > sprite2.x and
                sprite1.y < sprite2.y + sprite2.height and
                sprite1.y + sprite1.height > sprite2.y)

    def draw_text(self, text, x, y, color="black", size=12, font="Arial", anchor="center"):
        if anchor == "center":
            text_anchor = "center"
        elif anchor == "left":
            text_anchor = "w"
        elif anchor == "right":
            text_anchor = "e"
        elif anchor == "top":
            text_anchor = "n"
        elif anchor == "bottom":
            text_anchor = "s"
        elif anchor == "top left":
            text_anchor = "nw"
        elif anchor == "top right":
            text_anchor = "ne"
        elif anchor == "bottom left":
            text_anchor = "sw"
        elif anchor == "bottom right":
            text_anchor = "se"
        else:
            text_anchor = "center"

        self.canvas.create_text(x, y, text=text, fill=color, font=(font, size), anchor=text_anchor)

    def draw_rectangle(self, x, y, width, height, color="black", fill=True):
        if fill:
            self.canvas.create_rectangle(x, y, x + width, y + height, fill=color, outline=color)
        else:
            self.canvas.create_rectangle(x, y, x + width, y + height, outline=color)

    def draw_circle(self, x, y, radius, color="black", fill=True):
        if fill:
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline=color)
        else:
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline=color)

    def random_number(self, min_val, max_val):
        return random.randint(min_val, max_val)

    def title(self, title):
        self.title(title)

    def freeze(self, duration=None):
        self.is_frozen = True
        if duration:
            self.root.after(int(duration * 1000), self.unfreeze)

    def unfreeze(self):
        self.is_frozen = False

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y2) ** 2)

    def optimize(self, sprites_to_cull):
        for sprite in sprites_to_cull:
            if sprite in self.sprites:
                self.sprites.remove(sprite)
                print(f"Sprite culled: {sprite}")

    class experimental:
        def pen_down(self, sprite, color="black", width=1):
            sprite.pen_active = True
            sprite.pen_color = color
            sprite.pen_width = width
            sprite.last_pen_x = sprite.x + sprite.anchor_x_offset
            sprite.last_pen_y = sprite.y + sprite.anchor_y_offset

        def pen_up(self, sprite):
            sprite.pen_active = False

        def pen(self, sprite, active=True, color="black", width=1):
            if active:
                self.pen_down(sprite, color, width)
            else:
                self.pen_up(sprite)

        def clear_pen_lines(self):
            self.pen_lines = []


class Sprite:
    def __init__(self, game, image_path=None, x=0, y=0, width=50, height=50, color="blue"):
        self.game = game
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.visible = True
        self.direction = 90
        self.speed = 0
        self.image = None
        self.image_object = None
        self.rotate = 0
        self.rotate_visual = False

        self.anchor = "center"
        self.anchor_x_offset = self.width / 2
        self.anchor_y_offset = self.height / 2

        self.pen_active = False
        self.pen_color = "black"
        self.pen_width = 1
        self.last_pen_x = x + self.anchor_x_offset
        self.last_pen_y = y + self.anchor_y_offset

        if image_path:
            self.set_image(image_path)

        self.on_update = None

        self.layer = 0

        self._transform_active = False
        self._transform_start_time = 0
        self._transform_duration = 0
        self._transform_start_values = {}
        self._transform_end_values = {}
        self._transform_easing = "linear"

    def set_layer(self, layer):
        self.layer = layer

    def set_image(self, image_path):
        try:
            pil_image = Image.open(image_path)
            pil_image = pil_image.resize((self.width, self.height), Image.LANCZOS)
            self.image_object = ImageTk.PhotoImage(pil_image)
            self.image = image_path
        except Exception as e:
            print(f"Error loading image: {e}")
            self.image = None
            self.image_object = None

    def set_anchor(self, anchor):
        if isinstance(anchor, (list, tuple)) and len(anchor) == 2:
            self.anchor_x_offset = anchor[0]
            self.anchor_y_offset = anchor[1]
            self.anchor = "custom"
        else:
            self.anchor = anchor.lower()

            if self.anchor == "center":
                self.anchor_x_offset = self.width / 2
                self.anchor_y_offset = self.height / 2
            elif self.anchor == "left":
                self.anchor_x_offset = 0
                self.anchor_y_offset = self.height / 2
            elif self.anchor == "right":
                self.anchor_x_offset = self.width
                self.anchor_y_offset = self.height / 2
            elif self.anchor == "top":
                self.anchor_x_offset = self.width / 2
                self.anchor_y_offset = 0
            elif self.anchor == "bottom":
                self.anchor_x_offset = self.width / 2
                self.anchor_y_offset = self.height
            elif self.anchor == "top left":
                self.anchor_x_offset = 0
                self.anchor_y_offset = 0
            elif self.anchor == "top right":
                self.anchor_x_offset = self.width
                self.anchor_y_offset = 0
            elif self.anchor == "bottom left":
                self.anchor_x_offset = 0
                self.anchor_y_offset = self.height
            elif self.anchor == "bottom right":
                self.anchor_x_offset = self.width
                self.anchor_y_offset = self.height
            else:
                self.anchor = "center"
                self.anchor_x_offset = self.width / 2
                self.anchor_y_offset = self.height / 2

    def update(self):
        current_x = self.x + self.anchor_x_offset
        current_y = self.y + self.anchor_y_offset

        angle_rad = math.radians(self.direction)
        self.x += self.speed * math.cos(angle_rad)
        self.y += self.speed * math.sin(angle_rad)

        if self._transform_active:
            self._apply_transformation()

        if self.pen_active:
            new_x = self.x + self.anchor_x_offset
            new_y = self.y + self.anchor_y_offset

            if (new_x != self.last_pen_x or new_y != self.last_pen_y) and self.visible:
                self.game.pen_lines.append({
                    "x1": self.last_pen_x,
                    "y1": self.last_pen_y,
                    "x2": new_x,
                    "y2": new_y,
                    "color": self.pen_color,
                    "width": self.pen_width
                })

                self.game.canvas.create_line(
                    self.last_pen_x, self.last_pen_y,
                    new_x, new_y,
                    fill=self.pen_color,
                    width=self.pen_width
                )

            self.last_pen_x = new_x
            self.last_pen_y = new_y

        if self.on_update:
            self.on_update()

    def draw(self, canvas):
        if not self.visible:
            return

        if self.image_object:
            canvas.create_image(self.x, self.y, image=self.image_object, anchor="nw")
        else:
            if self.rotate_visual:
                anchor_absolute_x = self.x + self.anchor_x_offset
                anchor_absolute_y = self.y + self.anchor_y_offset

                angle_rad = math.radians(self.rotate)
                cos_val = math.cos(angle_rad)
                sin_val = math.sin(angle_rad)

                corners = [
                    (-self.anchor_x_offset, -self.anchor_y_offset),
                    (self.width - self.anchor_x_offset, -self.anchor_y_offset),
                    (self.width - self.anchor_x_offset, self.height - self.anchor_y_offset),
                    (-self.anchor_x_offset, self.height - self.anchor_y_offset)
                ]

                points = []
                for corner_x, corner_y in corners:
                    rotated_x = corner_x * cos_val - corner_y * sin_val
                    rotated_y = corner_x * sin_val + corner_y * cos_val

                    points.extend([anchor_absolute_x + rotated_x, anchor_absolute_y + rotated_y])

                canvas.create_polygon(points, fill=self.color, outline=self.color)
            else:
                canvas.create_rectangle(
                    self.x, self.y,
                    self.x + self.width, self.y + self.height,
                    fill=self.color, outline=self.color
                )

    def move(self, x, y):
        if self.pen_active:
            self.last_pen_x = self.x + self.anchor_x_offset
            self.last_pen_y = self.y + self.anchor_y_offset

        self.x += x
        self.y += y

        if self.pen_active and self.visible:
            new_x = self.x + self.anchor_x_offset
            new_y = self.y + self.anchor_y_offset

            self.game.pen_lines.append({
                "x1": self.last_pen_x,
                "y1": self.last_pen_y,
                "x2": new_x,
                "y2": new_y,
                "color": self.pen_color,
                "width": self.pen_width
            })

            self.last_pen_x = new_x
            self.last_pen_y = new_y

    def move_to(self, x, y):
        if self.pen_active:
            self.last_pen_x = self.x + self.anchor_x_offset
            self.last_pen_y = self.y + self.anchor_y_offset

        self.x = x
        self.y = y

        if self.pen_active and self.visible:
            new_x = self.x + self.anchor_x_offset
            new_y = self.y + self.anchor_y_offset

            self.game.pen_lines.append({
                "x1": self.last_pen_x,
                "y1": self.last_pen_y,
                "x2": new_x,
                "y2": new_y,
                "color": self.pen_color,
                "width": self.pen_width
            })

            self.last_pen_x = new_x
            self.last_pen_y = new_y

    def move_forward(self, distance):
        if self.pen_active:
            self.last_pen_x = self.x + self.anchor_x_offset
            self.last_pen_y = self.y + self.anchor_y_offset

        angle_rad = math.radians(self.direction)
        self.x += distance * math.cos(angle_rad)
        self.y += distance * math.sin(angle_rad)

        if self.pen_active and self.visible:
            new_x = self.x + self.anchor_x_offset
            new_y = self.y + self.anchor_y_offset

            self.game.pen_lines.append({
                "x1": self.last_pen_x,
                "y1": self.last_pen_y,
                "x2": new_x,
                "y2": new_y,
                "color": self.pen_color,
                "width": self.pen_width
            })

            self.last_pen_x = new_x
            self.last_pen_y = new_y

    def turn(self, angle):
        self.direction += angle

    def point_towards(self, x, y, rotate_visual=False):
        anchor_absolute_x = self.x + self.anchor_x_offset
        anchor_absolute_y = self.y + self.anchor_y_offset

        dx = x - anchor_absolute_x
        dy = y - anchor_absolute_y
        self.direction = math.degrees(math.atan2(dy, dx))
        self.rotate_visual = rotate_visual

    def turn_towards(self, target_x, target_y, turn_speed, rotate_visual=True):
        anchor_absolute_x = self.x + self.anchor_x_offset
        anchor_absolute_y = self.y + self.anchor_y_offset

        dx = target_x - anchor_absolute_x
        dy = target_y - anchor_absolute_y
        target_angle = math.degrees(math.atan2(dy, dx))

        angle_diff = (target_angle - self.direction + 360) % 360
        if angle_diff > 180:
            angle_diff -= 360

        if abs(angle_diff) < turn_speed:
            self.direction = target_angle
        else:
            self.direction += turn_speed if angle_diff > 0 else -turn_speed
        self.rotate_visual = rotate_visual

    def set_size(self, width, height):
        old_width = self.width
        old_height = self.height

        self.width = width
        self.height = height

        if self.anchor == "custom":
            self.anchor_x_offset = (self.anchor_x_offset / old_width) * width
            self.anchor_y_offset = (self.anchor_y_offset / old_height) * height
        else:
            self.set_anchor(self.anchor)

        if self.image:
            self.set_image(self.image)

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def is_touching(self, other_sprite):
        return self.game.check_collision(self, other_sprite)

    def is_touching_edge(self):
        return (self.x <= 0 or
                self.y <= 0 or
                self.x + self.width >= self.game.width or
                self.y + self.height >= self.game.height)

    def on_hover(self):
        if self.x < self.game.mouse_x < self.x + self.width and self.y < self.game.mouse_y < self.y + self.height:
            return True

    def transform(self, duration=1, transform="linear", **kwargs):
        self._transform_active = True
        self._transform_start_time = time.time()
        self._transform_duration = duration
        self._transform_start_values = {}
        self._transform_end_values = {}
        self._transform_easing = transform

        for property, end_value in kwargs.items():
            if hasattr(self, property):
                self._transform_start_values[property] = getattr(self, property)
                self._transform_end_values[property] = end_value
            else:
                print(f"Warning: Sprite does not have property '{property}'")

    def _apply_transformation(self):
        elapsed_time = time.time() - self._transform_start_time
        progress = min(1, elapsed_time / self._transform_duration)

        if self._transform_easing == "linear":
            eased_progress = progress
        elif self._transform_easing == "ease_in":
            eased_progress = progress ** 2
        elif self._transform_easing == "ease_out":
            eased_progress = 1 - (1 - progress) ** 2
        elif self._transform_easing == "ease_in_out":
            if progress < 0.5:
                eased_progress = 2 * progress ** 2
            else:
                eased_progress = 1 - ((-2 * progress + 2) ** 2) / 2
        else:
            eased_progress = progress

        for property, start_value in self._transform_start_values.items():
            end_value = self._transform_end_values[property]

            if property == "color":
                if isinstance(start_value, str) and start_value.startswith("#"):
                    r1, g1, b1 = self._hex_to_rgb(start_value)
                    r2, g2, b2 = self._hex_to_rgb(end_value)

                    r = int(r1 + (r2 - r1) * eased_progress)
                    g = int(g1 + (g2 - g1) * eased_progress)
                    b = int(b1 + (b2 - b1) * eased_progress)

                    setattr(self, property, self._rgb_to_hex(r, g, b))
                else:
                    print(f"Warning: Cannot transform color from {start_value}.  Must be a hex code.")
                    self._transform_active = False
                    return

            elif property == "rotate":
                setattr(self, property, start_value + (end_value - start_value) * eased_progress)
                self.rotate_visual = True

            elif property == "direction":
                setattr(self, property, start_value + (end_value - start_value) * eased_progress)

            else:
                setattr(self, property, start_value + (end_value - start_value) * eased_progress)

        if progress >= 1:
            self._transform_active = False

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, r, g, b):
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def add_rotation(self, angle):
      self.rotate += angle
      self.rotate_visual = True

    def set_rotation(self, angle):
      self.rotate = angle
      self.rotate_visual = True


if __name__ == "__main__":
    game = SimplePy(title="My First Game", width=800, height=600)

    player = game.create_sprite(x=400, y=300, width=50, height=50, color="#FF0000")
    player.set_layer(1)

    def start():
        print("Game started!")

    def update():
        if game.is_key_pressed("left"):
            player.move(-5, 0)
        if game.is_key_pressed("right"):
            player.move(5, 0)
        if game.is_key_pressed("up"):
            player.move(0, -5)
        if game.is_key_pressed("down"):
            player.move(0, 5)

        if game.mouse_pressed:
            player.point_towards(game.mouse_x, game.mouse_y)
            player.speed = 3
        else:
            player.speed = 0

        if game.is_key_pressed("f"):
            game.freeze(3)

        if game.is_key_pressed("t"):
            player.transform(width=100, height=100, color="#00FF00", transform="ease_in_out", duration=2)

        if game.is_key_pressed("r"):
            player.transform(rotate=360, transform="linear", duration=3)

        if game.is_key_pressed("e"):
            player.transform(direction=180, transform="linear", duration=3)

        if player.on_hover():
            print("LOL")

    def draw():
        game.draw_text(f"Mouse: ({game.mouse_x}, {game.mouse_y})", 20, 20, anchor="left")
        game.draw_text("Use arrow keys to move or click to follow mouse", 20, 40, anchor="left")
        game.draw_text("Press f to freeze the game", 20, 60, anchor="left")
        game.draw_text("Press t to transform the square", 20, 80, anchor="left")
        game.draw_text("Press r to rotate the square", 20, 100, anchor="left")
        game.draw_text("Press e to set direction", 20, 120, anchor="left")
        game.draw_text(f"FPS: {game.current_fps}", 700, 20, anchor="topleft")
        if game.is_frozen:
            game.draw_text("FROZEN", game.width / 2, game.height / 2, color="black", size=30)
            player.set_layer(0)
        else:
            player.set_layer(1)

    game.on_start = start
    game.on_update = update
    game.on_draw = draw

    game.run()