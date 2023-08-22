import cv2
import tkinter as tk
import math
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk


class CircularSlider:
    def __init__(self, parent, width=150):
        self.parent = parent
        self.width = width
        self.radius = self.width / 2
        self.angle = 0
        self.value = 0

        self.canvas = tk.Canvas(parent, width=self.width, height=self.width)
        self.canvas.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        self.canvas.grid_remove()  # Hiding the circular slider initially

        self.canvas.create_oval(5, 5, self.width - 5, self.width - 5, outline='gray', width=2)
        self.handle = self.canvas.create_line(self.radius, self.radius, self.radius, 10, fill='red', width=2)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)

    def on_canvas_click(self, event):
        self.update_slider(event.x, event.y)

    def on_canvas_drag(self, event):
        self.update_slider(event.x, event.y)

    def update_slider(self, x, y):
        dx = x - self.radius
        dy = y - self.radius
        angle = math.degrees(math.atan2(dy, dx)) % 360
        self.angle = angle
        self.value = 360 - angle
        self.canvas.coords(self.handle, self.radius, self.radius, x, y)

    def get_value(self):
        return self.value


class ImageApp:
    def __init__(self, Root):
        self.root = Root
        self.root.title("TheImageProject")

        # Attributes for modified images
        self.resized_image = None
        self.rotated_image = None
        self.flipped_image = None

        self.image = None

        # Styling the window
        self.root.geometry("800x500")
        self.root.configure(bg="#ffffff")

        self.canvas = tk.Canvas(Root, width=400, height=400, bg="white")
        self.canvas.grid(row=0, column=0, rowspan=5, padx=20, pady=20)

        self.load_button = ttk.Button(Root, text="Load Image", command=self.load_image)
        self.load_button.grid(row=0, column=1, padx=20, pady=10, sticky="w")

        self.resize_button = ttk.Button(Root, text="Resize Image", command=self.resize_image)
        self.resize_button.grid(row=1, column=1, padx=20, pady=10, sticky="w")

        self.rotate_button = ttk.Button(Root, text="Rotate Image", command=self.rotate_image)
        self.rotate_button.grid(row=2, column=1, padx=20, pady=10, sticky="w")

        self.flip_button = ttk.Button(Root, text="Flip Image", command=self.flip_image)
        self.flip_button.grid(row=3, column=1, padx=20, pady=10, sticky="w")

        self.rotate_slider = CircularSlider(Root, width=100)
        self.rotate_slider.canvas.grid(row=2, column=2, padx=20, pady=10, sticky="w")

        self.save_button = ttk.Button(Root, text="Save Image", command=self.save_image)
        self.save_button.grid(row=4, column=1, padx=20, pady=10, sticky="w")

        # Create footer label
        footer_label = tk.Label(Root, text="Developed by: Abhishek Shah", font=("Helvetica", 10), bg="#f0f0f0")
        footer_label.grid(row=6, column=1, columnspan=5, padx=80, pady=(10, 0), sticky="s")

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            self.image = cv2.imread(file_path)
            self.display_image(self.image)

    def display_image(self, img):
        img_height, img_width = img.shape[:2]
        max_canvas_width = 400
        max_canvas_height = 400
        scale_factor = min(max_canvas_width / img_width, max_canvas_height / img_height)
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img.resize((new_width, new_height)))

        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.image = img

    def resize_image(self):
        if self.image is not None:
            # Create a custom dialog box for resizing
            dialog = tk.Toplevel(self.root)
            dialog.title("Resize Image")

            width_label = tk.Label(dialog, text="New Width:")
            width_label.grid(row=0, column=0, padx=10, pady=5)

            width_entry = tk.Entry(dialog)
            width_entry.grid(row=0, column=1, padx=10, pady=5)

            height_label = tk.Label(dialog, text="New Height:")
            height_label.grid(row=1, column=0, padx=10, pady=5)

            height_entry = tk.Entry(dialog)
            height_entry.grid(row=1, column=1, padx=10, pady=5)

            resize_button = ttk.Button(dialog, text="Resize",
                                       command=lambda: self.perform_resizing(dialog, width_entry, height_entry))
            resize_button.grid(row=2, columnspan=2, padx=10, pady=10)

    def perform_resizing(self, dialog, width_entry, height_entry):
        new_width_str = width_entry.get()
        new_height_str = height_entry.get()

        try:
            new_width = int(new_width_str)
            new_height = int(new_height_str)
            if new_width > 0 and new_height > 0:
                self.resized_image = cv2.resize(self.image, (new_width, new_height))
                self.display_image(self.resized_image)
                dialog.destroy()  # Close the dialog box after resizing
            else:
                tk.messagebox.showerror("Error", "Dimensions must be greater than zero.")
        except (ValueError, TypeError):
            tk.messagebox.showerror("Error", "Invalid dimension values. Please enter valid integers.")

    def rotate_image(self):
        if self.image is not None:
            angle = self.rotate_slider.get_value()
            rotation_matrix = cv2.getRotationMatrix2D((self.image.shape[1] / 2, self.image.shape[0] / 2), angle, 1)
            self.rotated_image = cv2.warpAffine(self.image, rotation_matrix, (self.image.shape[1], self.image.shape[0]))
            self.display_image(self.rotated_image)

    def show_rotate_slider(self):
        self.rotate_slider.canvas.grid()

    def flip_image(self):
        if self.image is not None:
            dialog = tk.Toplevel(self.root)
            dialog.title("Flip Image")

            flip_var = tk.IntVar()  # Variable to store the user's choice

            tk.Label(dialog, text="Choose flip direction:").pack()

            tk.Radiobutton(dialog, text="Horizontal", variable=flip_var, value=1).pack()
            tk.Radiobutton(dialog, text="Vertical", variable=flip_var, value=0).pack()

            flip_button = ttk.Button(dialog, text="Flip", command=lambda: self.perform_flipping(dialog, flip_var))
            flip_button.pack()

    def perform_flipping(self, dialog, flip_var):
        flip_direction = flip_var.get()

        if flip_direction == 1:  # Horizontal flip OpenCV value = 1
            self.flipped_image = cv2.flip(self.image, flip_direction)

        elif flip_direction == 0:  # Vertical flip OpenCV value = 0
            self.flipped_image = cv2.flip(self.image, flip_direction)
        else:
            dialog.destroy()
            return

        self.display_image(self.flipped_image)
        dialog.destroy()  # Close the dialog box after flipping

    def apply_modifications(self, image):
        edited_image = image.copy()

        if self.resized_image is not None:
            edited_image = self.resized_image
        if self.rotated_image is not None:
            edited_image = self.rotated_image
        if self.flipped_image is not None:
            edited_image = self.flipped_image

        return edited_image

    def save_image(self):
        if self.image is not None:
            modified_image = self.apply_modifications(self.image)
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")])
            if file_path:
                # Modified piece for trying filtered image
                # cv2.imwrite(file_path, cv2.cvtColor(modified_image, cv2.COLOR_RGB2BGR))
                cv2.imwrite(file_path, modified_image)
                messagebox.showinfo("Save Image", "Image saved successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()
