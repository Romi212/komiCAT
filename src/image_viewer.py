import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog, ttk

from text_extractor import TextExtractor
from aux_types.text_box import TextBox
from aux_types.text_box_button import TextBoxButton
from views_adapter import ViewsAdapter

class ImageViewer:
    def __init__(self, parent):
        self.text_extractor = TextExtractor()
        self.detected_bubbles = []  
        self.detected_text_areas_buttons = []
        self.detected_text_bubbles = []
        self.detected_free_text = []
        self.selected_bubbles = []  
        # Current image and zoom
        self.original_image = None
        self.current_image = None
        self.zoom_factor = 1.0

        # Create scrollable canvas
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame, bg='gray')
        self.h_scroll = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scroll = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Button frame
        self.button_frame = ttk.Frame(parent)
        self.button_frame.pack(fill=tk.X)

        self.open_button = ttk.Button(self.button_frame, text="Open Image", command=self.load_image)
        self.open_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.zoom_in_button = ttk.Button(self.button_frame, text="Zoom In", command=self.zoom_in)
        self.zoom_in_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.zoom_out_button = ttk.Button(self.button_frame, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.reset_zoom_button = ttk.Button(self.button_frame, text="Reset Zoom", command=self.reset_zoom)
        self.reset_zoom_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.detect_bubbles_button = ttk.Button(self.button_frame, text="Detect Bubbles", command=self.detect_bubbles)
        self.detect_bubbles_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.extract_text_button = ttk.Button(self.button_frame, text="Extract Text", command=self.extract_text)
        self.extract_text_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Bind mouse wheel for zooming
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        # Status label
        self.status_label = ttk.Label(parent, text="Ready")
        self.status_label.pack(pady=5)

    def set_adapter(self, adapter):
        self.adapter = adapter
    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Open Image File",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.ico")]
        )
        if file_path:
            self.original_image = Image.open(file_path)
            self.zoom_factor = 1.0
            self.update_image()
            self.status_label.config(text=f"Loaded: {file_path}")

    def update_image(self):
        if self.original_image:
            # Calculate new size
            new_width = int(self.original_image.width * self.zoom_factor)
            new_height = int(self.original_image.height * self.zoom_factor)

            # Resize image
            self.current_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.current_image)

            # Clear canvas and add new image
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

            # Update scroll region
            self.canvas.config(scrollregion=(0, 0, new_width, new_height))

            self.status_label.config(text=f"Zoom: {self.zoom_factor:.2f}x")

    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.update_image()

    def zoom_out(self):
        self.zoom_factor /= 1.2
        self.update_image()

    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.update_image()

    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
            
    def selected_bubble(self, bubble_button):
        print(f"Selected bubble")
        if bubble_button not in self.selected_bubbles:
            self.selected_bubbles.append(bubble_button)
            bubble_button.selected(len(self.selected_bubbles))
            
        


    def detect_bubbles(self):
        if self.current_image:
            self.detected_bubbles, self.detected_text_bubbles, self.detected_free_text = self.text_extractor.detect_speech_bubbles(self.current_image)
            for bubble in self.detected_text_bubbles:
                button = TextBoxButton( bubble, lambda: None)
                button.config(command=lambda b=button: self.selected_bubble(b))
                self.detected_text_areas_buttons.append(button)
                self.canvas.create_window((bubble.xmin + bubble.xmax)// 2, bubble.ymin, window=button)
                self.canvas.create_rectangle(bubble.xmin, bubble.ymin, bubble.xmax, bubble.ymax, outline='red', width=2)
            for bubble in self.detected_free_text:
                self.canvas.create_rectangle(bubble.xmin, bubble.ymin, bubble.xmax, bubble.ymax, outline='blue', width=2)

    def extract_text(self):
        if (self.detected_text_bubbles or self.detected_free_text) and self.current_image:
            if(len(self.selected_bubbles) == 0):
                print("No bubbles selected, extracting text from all detected bubbles")
            else:
                self.text_extractor.extract_text(self.current_image, [button.text_box for button in self.selected_bubbles])
                self.adapter.AddSegments(self.selected_bubbles)

           
           