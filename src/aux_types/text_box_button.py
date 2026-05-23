
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt


class TextBoxButton(QPushButton):
    def __init__(self, text_box, onClick, width=80, height=30, alpha=0.6):
        super().__init__()
        self.text_box = text_box
        self.text = ""
        self.number = 0
        self.clicked.connect(onClick)
        
        # Set fixed size
        self.setFixedSize(width, height)

        bg_color,  hover_color, pressed_color, border_color= self.choose_colors(text_box.label)
        
        # Apply styling with transparency
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 4px;
                color: {border_color};
                font-weight: bold;
                font-size: 50px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """)

    def selected(self, number):
        print(number)
        self.number = number
        self.text = f"{number}"
        self.setText(f"{number}")


    def choose_colors(self, label):
        background = 200
        selected = 180
        pressed = 160
        transparency = 0.2
        if label == "text_bubble":
            return f"rgba({background}, 0, 0, {transparency})", f"rgba({selected}, 0, 0, {transparency})", f"rgba({pressed}, 0, 0, {transparency})", "red"
        elif label == "free_text":
            return f"rgba(0, 0, {background}, {transparency})", f"rgba(0, 0, {selected}, {transparency})", f"rgba(0, 0, {pressed}, {transparency})", "blue"
        else:
            return f"rgba(0, {background}, 0, {transparency})", f"rgba(0, {selected}, 0, {transparency})", f"rgba(0, {pressed}, 0, {transparency})", "green"

    
