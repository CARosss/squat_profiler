import tkinter as tk
from tkinter import ttk
import math


class SquatSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Bottom Position Squat Simulator")

        # Fixed ankle position
        self.ankle_x = 200
        self.ankle_y = 250

        # Adjustable parameters
        self.femur_length = tk.DoubleVar(value=50)  # cm
        self.tibia_length = tk.DoubleVar(value=40)  # cm
        self.torso_length = tk.DoubleVar(value=55)  # cm
        self.bar_position = tk.DoubleVar(value=0.85)  # % up torso from hip
        self.ankle_angle = tk.DoubleVar(value=-20)  # degrees from vertical
        self.hip_angle = tk.DoubleVar(value=10)  # degrees of hip opening

        # Value display variables
        self.femur_display = tk.StringVar()
        self.tibia_display = tk.StringVar()
        self.torso_display = tk.StringVar()
        self.bar_display = tk.StringVar()
        self.ankle_angle_display = tk.StringVar()
        self.hip_angle_display = tk.StringVar()

        # Create frames and canvas
        control_frame = ttk.Frame(root, padding="10")
        control_frame.grid(row=0, column=0, sticky="nsew")

        canvas_frame = ttk.Frame(root, padding="10")
        canvas_frame.grid(row=0, column=1, sticky="nsew")

        self.canvas = tk.Canvas(canvas_frame, width=400, height=400, bg='white')
        self.canvas.grid(row=0, column=0)

        # Create sliders with value displays
        self.create_slider_with_value(control_frame, "Femur Length (cm)", self.femur_length, 35, 55, 0,
                                      self.femur_display)
        self.create_slider_with_value(control_frame, "Tibia Length (cm)", self.tibia_length, 35, 55, 1,
                                      self.tibia_display)
        self.create_slider_with_value(control_frame, "Torso Length (cm)", self.torso_length, 40, 65, 2,
                                      self.torso_display)
        self.create_slider_with_value(control_frame, "Bar Position (% up torso)", self.bar_position, 0.3, 1, 3,
                                      self.bar_display)
        self.create_slider_with_value(control_frame, "Ankle Angle (deg)", self.ankle_angle, -60, 60, 4,
                                      self.ankle_angle_display)
        self.create_slider_with_value(control_frame, "Hip Width Angle (deg)", self.hip_angle, 0, 90, 5,
                                      self.hip_angle_display)

        # Add debug text
        self.debug_text = tk.StringVar()
        ttk.Label(control_frame, textvariable=self.debug_text, wraplength=200).grid(row=7, column=0, columnspan=3)

        self.update_figure()

    def create_slider_with_value(self, parent, label, variable, min_val, max_val, row, display_var):
        ttk.Label(parent, text=label, width=20).grid(row=row, column=0, sticky="w")
        slider = ttk.Scale(parent, from_=min_val, to=max_val, orient="horizontal",
                           variable=variable, command=lambda _: self.update_all())
        slider.grid(row=row, column=1, sticky="ew", padx=5)
        ttk.Label(parent, textvariable=display_var, width=6).grid(row=row, column=2, sticky="e", padx=5)

    def update_all(self):
        # Update value displays
        self.femur_display.set(f"{self.femur_length.get():.1f}")
        self.tibia_display.set(f"{self.tibia_length.get():.1f}")
        self.torso_display.set(f"{self.torso_length.get():.1f}")
        self.bar_display.set(f"{self.bar_position.get():.2f}")
        self.ankle_angle_display.set(f"{self.ankle_angle.get():.1f}")
        self.hip_angle_display.set(f"{self.hip_angle.get():.1f}")
        # Update figure
        self.update_figure()

    def draw_angle(self, x, y, start_angle, end_angle, radius=20, color="gray"):
        # Convert angles to radians for calculation
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)

        # Calculate arc points
        start_x = x + radius * math.cos(start_rad)
        start_y = y - radius * math.sin(start_rad)
        end_x = x + radius * math.cos(end_rad)
        end_y = y - radius * math.sin(end_rad)

        # Draw the arc
        self.canvas.create_arc(x - radius, y - radius, x + radius, y + radius,
                               start=start_angle, extent=end_angle - start_angle,
                               style="arc", outline=color)

    def calculate_positions(self):
        scale = 2  # Scale factor for visualization

        # Get scaled lengths
        tibia = self.tibia_length.get() * scale

        actual_femur = self.femur_length.get() * scale
        # Apply hip angle projection
        hip_angle_rad = math.radians(self.hip_angle.get())
        femur = actual_femur * math.cos(hip_angle_rad)

        torso = self.torso_length.get() * scale

        # Calculate knee position using ankle angle
        ankle_angle_rad = math.radians(self.ankle_angle.get())
        knee_x = self.ankle_x + tibia * math.sin(ankle_angle_rad) * math.cos(hip_angle_rad)
        knee_y = self.ankle_y - tibia * math.cos(ankle_angle_rad)

        # Step 2: Place hip
        hip_x = knee_x + femur  # Using projected femur length
        hip_y = knee_y

        # Step 3: Calculate shoulder position
        dx_to_bar = self.ankle_x - hip_x
        shoulder_dx = dx_to_bar / self.bar_position.get()
        torso_calc = torso ** 2 - shoulder_dx ** 2
        shoulder_dy = math.sqrt(torso_calc)
        shoulder_x = hip_x + shoulder_dx
        shoulder_y = hip_y - shoulder_dy

        # Step 4: Calculate bar position
        bar_x = self.ankle_x
        bar_y = hip_y - (shoulder_dy * self.bar_position.get())

        return {
            'ankle': (self.ankle_x, self.ankle_y),
            'knee': (knee_x, knee_y),
            'hip': (hip_x, hip_y),
            'shoulder': (shoulder_x, shoulder_y),
            'bar': (bar_x, bar_y)
        }

    def update_figure(self):
        self.canvas.delete("all")
        self.canvas.create_line(100, self.ankle_y, 300, self.ankle_y, fill='gray', width=2)

        try:
            positions = self.calculate_positions()

            # Draw vertical reference line
            self.canvas.create_line(
                self.ankle_x, self.ankle_y - 150,
                self.ankle_x, self.ankle_y + 10,
                fill='gray', dash=(2, 2)
            )

            # Draw segments
            segments = [('ankle', 'knee'), ('knee', 'hip'), ('hip', 'shoulder')]
            for start, end in segments:
                self.canvas.create_line(
                    positions[start][0], positions[start][1],
                    positions[end][0], positions[end][1],
                    width=3, fill='black'
                )

            # Draw angles at knee and hip
            knee = positions['knee']
            hip = positions['hip']
            ankle = positions['ankle']
            shoulder = positions['shoulder']

            # Calculate and draw angles
            # Shin angle from vertical
            shin_angle = math.degrees(math.atan2(knee[0] - ankle[0], knee[1] - ankle[1]))
            self.draw_angle(knee[0], knee[1], 180, 180 + shin_angle)
            self.canvas.create_text(knee[0] - 30, knee[1],
                                    text=f"{abs(shin_angle):.0f}°", fill="gray")

            # Torso angle from vertical
            torso_angle = math.degrees(math.atan2(shoulder[0] - hip[0], shoulder[1] - hip[1]))
            self.draw_angle(hip[0], hip[1], 180, 180 + torso_angle)
            self.canvas.create_text(hip[0] - 30, hip[1],
                                    text=f"{abs(torso_angle):.0f}°", fill="gray")

            # Draw hip opening angle indication
            if self.hip_angle.get() > 0:
                self.canvas.create_text(hip[0] - 5, hip[1] + 20,
                                        text=f"Hip {self.hip_angle.get():.0f}°", fill="blue")

            # Draw bar
            bar_radius = 8
            self.canvas.create_oval(
                positions['bar'][0] - bar_radius, positions['bar'][1] - bar_radius,
                positions['bar'][0] + bar_radius, positions['bar'][1] + bar_radius,
                fill='blue', outline='blue'
            )

            # Draw joints
            joint_radius = 5
            for point in positions.values():
                self.canvas.create_oval(
                    point[0] - joint_radius, point[1] - joint_radius,
                    point[0] + joint_radius, point[1] + joint_radius,
                    fill='red', outline='red'
                )

            self.debug_text.set("Valid position")

        except Exception as e:
            self.debug_text.set(f"Error: {str(e)}")


def main():
    root = tk.Tk()
    app = SquatSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()