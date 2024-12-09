import math
import tkinter as tk
from tkinter import ttk
from turtle import TurtleScreen, ScrolledCanvas, Screen

from fingerprint import Fingerprint
from tortoise import Tortoise, Scale, Translate


class FingerprintGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fingerprint Texture Generator")

        # Create the main frame to hold the Turtle canvas and the controls
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # Create a canvas for the Turtle screen
        # TODO unfortunately this only saves the shown region. Increase window size as a quick fix
        self.canvas = ScrolledCanvas(self.main_frame, 1000, 1000, 1000, 1000)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Initialize the Turtle screen within the Tkinter canvas
        self.screen = TurtleScreen(self.canvas)
        self.screen.screensize(1000, 1000)
        self.screen.tracer(0, 0)
        self.screen.bgcolor("white")

        # Create a turtle for drawing
        self.turtle = Tortoise(self.screen)
        self.turtle.add_transform(Scale(2.5))
        # self.turtle.add_transform(Translate((x + 0.5) * 180 - 90, -(y + 0.5) * 180 + 90))

        self.fingerprint = None

        # Create a control panel frame
        self.control_frame = tk.Frame(self.main_frame, padx=10, pady=10)
        self.control_frame.pack(side="right", fill="y")

        # Add sliders for parameters
        self.create_slider("seed", 0, 200, 3, resolution=1)
        self.create_slider("radius", 0, 5, 1.6, resolution=0.01)
        self.create_slider("num_poles", 0, 50, 20, resolution=1)
        self.create_slider("min_pole_strength", 10, 1000, 20, resolution=10)
        self.create_slider("max_pole_strength", 10, 1000, 100, resolution=10)
        self.create_slider("pole_distance_cutoff", 0, 500, 50, resolution=1)
        self.create_slider("global_flow_strength", 0, 1, 0.1, resolution=0.01)
        self.create_slider("global_flow_scale", 0.001, 0.1, 0.01, resolution=0.001)
        self.create_slider("max_path_length", 1, 100, 70, resolution=1)
        self.create_slider("max_tries", 100, 2000, 1000, resolution=10)

        self.show_steps = tk.BooleanVar()
        tk.Checkbutton(
            self.control_frame, text="Show Steps", variable=self.show_steps
        ).pack(pady=10)
        tk.Button(self.control_frame, text="Update", command=self.update).pack()
        tk.Button(self.control_frame, text="Save", command=self.save_fingerprint).pack()

    def create_slider(self, label, from_, to, initial, resolution=1):
        """Create a labeled slider and add it to the control frame."""
        slider = tk.Scale(
            self.control_frame,
            from_=from_,
            to=to,
            orient="horizontal",
            resolution=resolution,
        )
        slider.pack(pady=5)
        ttk.Label(self.control_frame, text=label).pack()
        slider.set(initial)
        setattr(self, f"{label.replace(' ', '_').lower()}_slider", slider)

    def update(self):
        """Update method to redraw the fingerprint. Customize this method as needed."""
        # Clear the previous drawing
        self.turtle.clear()
        self.turtle.penup()
        self.turtle.goto(0, 0)
        self.turtle.degrees(math.pi * 2)
        self.turtle.traveled = 0
        self.turtle.pendown()

        # Get the current slider values
        seed = self.seed_slider.get()
        radius = self.radius_slider.get()
        num_poles = self.num_poles_slider.get()
        min_pole_strength = self.min_pole_strength_slider.get()
        max_pole_strength = self.max_pole_strength_slider.get()
        pole_distance_cutoff = self.pole_distance_cutoff_slider.get()
        global_flow_strength = self.global_flow_strength_slider.get()
        global_flow_scale = self.global_flow_scale_slider.get()
        max_path_length = self.max_path_length_slider.get()
        max_tries = self.max_tries_slider.get()

        bbox = [int(x) for x in self.canvas.cget("scrollregion").split()]
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        self.fingerprint = Fingerprint(
            w,
            h,
            seed,
            radius,
            pole_distance_cutoff,
            global_flow_strength,
            global_flow_scale,
            max_path_length,
            max_tries,
        )

        self.fingerprint.add_random_poles(num_poles, min_pole_strength, max_pole_strength)

        print("Drawing...", end="")
        while self.fingerprint.draw(self.turtle):
            if self.show_steps.get():
                self.screen.update()

        self.screen.update()
        print(" Done!")

    def save_fingerprint(self):
        if not self.fingerprint:
            return

        # File dialog
        from tkinter import filedialog

        fp = self.fingerprint
        initial_filename = f"fingerprint_seed{fp.original_seed}_poles{len(fp.poles)}_radius{fp.radius:.2f}.eps"
        filename = filedialog.asksaveasfilename(
            initialfile=initial_filename,
            filetypes=(("EPS Files", "*.eps"), ("All Files", "*.*")),
            defaultextension=".eps",
        )
        if not filename:
            return

        print(f"Saving to {filename}")
        self.turtle.save_image(filename)


# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = FingerprintGUI(root)
    root.mainloop()
