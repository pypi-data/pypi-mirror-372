# coding: utf-8

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import json
import base64
import io

from image_grid_mark.resource_manager import ResourceManager
from image_grid_mark import __version__


class App(tk.Tk):
    def __init__(self, rm: ResourceManager):
        super().__init__()
        self.title(f"image_grid_mark V{__version__}")
        self.geometry("700x700")
        self.minsize(400, 400)
        self.iconphoto(False, tk.PhotoImage(file=rm.ico_path()))

        self.image = None
        self.photo = None
        self.canvas = None
        self.lines = []
        self.scale_factor = 1.0
        self.display_image_size = (0, 0)

        self.create_widgets()
        self.bind_events()

    def create_widgets(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        self.load_btn = tk.Button(button_frame, text="Load Image", command=self.load_image)
        self.load_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.load_json_btn = tk.Button(button_frame, text="Load JSON", command=self.load_json)
        self.load_json_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.save_btn = tk.Button(button_frame, text="Save JSON", command=self.save_json)
        self.save_btn.pack(side=tk.LEFT)
        self.save_btn.config(state=tk.DISABLED)

        self.canvas = tk.Canvas(main_frame, bg='white', cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.status = tk.StringVar()
        self.status.set("Load an image to start")
        status_bar = tk.Label(self, textvariable=self.status, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.add_vertical_line)
        self.canvas.bind("<Button-3>", self.add_horizontal_line)
        self.bind("r", self.remove_nearest_line)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )

        if not file_path:
            return

        try:
            self.image = Image.open(file_path)
            self.original_image = self.image.copy()
            self.display_image()
            self.lines.clear()
            self.save_btn.config(state=tk.NORMAL)
            self.status.set("Image loaded. LMB: vertical line, RMB: horizontal line, R: remove line")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def load_json(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            img_data = base64.b64decode(data['img'])
            self.image = Image.open(io.BytesIO(img_data))
            self.original_image = self.image.copy()

            self.lines.clear()
            self.canvas.delete("all")

            self.display_image()

            self.add_lines_from_data(data['table'])

            self.save_btn.config(state=tk.NORMAL)
            self.status.set("JSON loaded. Continue editing...")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON: {str(e)}")

    def add_lines_from_data(self, table_data):
        img_width, img_height = self.image.size

        for v_percent in table_data.get('v_lines', []):
            x_pos = v_percent * img_width * self.scale_factor
            line_id = self.canvas.create_line(x_pos, 0, x_pos, self.display_image_size[1],
                                              fill="red", width=2, tags="line")
            self.lines.append(("vertical", line_id, x_pos, 0, x_pos, self.display_image_size[1]))

        for h_percent in table_data.get('h_lines', []):
            y_pos = h_percent * img_height * self.scale_factor
            line_id = self.canvas.create_line(0, y_pos, self.display_image_size[0], y_pos,
                                              fill="blue", width=2, tags="line")
            self.lines.append(("horizontal", line_id, 0, y_pos, self.display_image_size[0], y_pos))

    def display_image(self):
        if not self.image:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 800
            canvas_height = 600

        img_width, img_height = self.image.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)

        self.display_image_size = (new_width, new_height)
        self.scale_factor = ratio

        resized_image = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_image)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.config(width=new_width, height=new_height)

        for line_type, line_id, x1, y1, x2, y2 in self.lines:
            if line_type == "vertical":
                self.canvas.create_line(x1, y1, x2, y2, fill="red", width=2, tags="line")
            else:
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2, tags="line")

    def add_vertical_line(self, event):
        if not self.image:
            return

        line_id = self.canvas.create_line(event.x, 0, event.x, self.display_image_size[1],
                                          fill="red", width=2, tags="line")

        self.lines.append(("vertical", line_id, event.x, 0, event.x, self.display_image_size[1]))

    def add_horizontal_line(self, event):
        if not self.image:
            return

        line_id = self.canvas.create_line(0, event.y, self.display_image_size[0], event.y,
                                          fill="blue", width=2, tags="line")

        self.lines.append(("horizontal", line_id, 0, event.y, self.display_image_size[0], event.y))

    def remove_nearest_line(self, event):
        if not self.lines:
            return

        canvas_x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        canvas_y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()

        nearest_line = None
        min_distance = float('inf')

        for line in self.lines[:]:
            line_type, line_id, x1, y1, x2, y2 = line

            if line_type == "vertical":
                distance = abs(canvas_x - x1)
            else:
                distance = abs(canvas_y - y1)

            if distance < min_distance:
                min_distance = distance
                nearest_line = line

        if nearest_line and min_distance < 20:
            line_type, line_id, x1, y1, x2, y2 = nearest_line
            self.canvas.delete(line_id)
            self.lines.remove(nearest_line)

    def save_json(self):
        if not self.image:
            return

        img_width, img_height = self.image.size
        v_lines = []
        h_lines = []

        for line_type, line_id, x1, y1, x2, y2 in self.lines:
            if line_type == "vertical":
                x_pos = (x1 / self.scale_factor) / img_width
                v_lines.append(round(x_pos, 4))
            else:
                y_pos = (y1 / self.scale_factor) / img_height
                h_lines.append(round(y_pos, 4))

        buffered = io.BytesIO()
        self.original_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        data = {
            "img": img_base64,
            "table": {
                "v_lines": sorted(v_lines),
                "h_lines": sorted(h_lines)
            }
        }

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                messagebox.showinfo("Success", "JSON file saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
