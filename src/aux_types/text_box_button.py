
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt


class TextBoxButton(QPushButton):
    def __init__(self, text_box, width=80, height=30, alpha=0.6):
        super().__init__()
        self.text_box = text_box
        self.text = ""
        self.number = 0
        self.onClick = None
        
        # Make button checkable to maintain pressed state
        self.setCheckable(True)
        
        # Connect to a wrapper that passes the button object instead of the boolean signal
        self.clicked.connect(self._on_clicked)
        
        # Set custom properties for state management
        self.setProperty("extracted", False)

        self.setProperty("focus", False)
        
        # Set fixed size
        self.setFixedSize(width, height)

        bg_color, hover_color, pressed_color, border_color = self.choose_colors(text_box.label)
        
        # Apply styling with custom property selectors
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 4px;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 2px 0px 0px 2px;
                text-align: left;
                margin: 0px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
            QPushButton:checked {{
                background-color: {pressed_color};
                border: 8px solid {border_color};
                border-radius: 16px;
            }}
            /* Custom state: extracted */
            QPushButton[extracted="true"] {{
                background-color: rgba(0, 0, 0, 0);
                border: 1px solid gray;
                color: transparent;
            }}
            QPushButton[extracted="true"]:hover {{
                background-color: rgba(0, 0, 0, 0);
            }}
            QPushButton[extracted="true"]:checked {{
                background-color: rgba(0, 0, 0, 0);
                border: 1px solid gray;
            }}
            /* Custom state: extracted AND focused */
            QPushButton[extracted="true", focus="true"] {{
                background-color: rgba(0, 0, 0, 0);
                border: 1px solid blue;
                color: transparent;
            }}
            QPushButton[extracted="true", focus="true"]:hover {{
                background-color: rgba(0, 0, 0, 0);
            }}
            QPushButton[extracted="true", focus="true"]:checked {{
                background-color: rgba(0, 0, 0, 0);
                border: 1px solid gray;
            }}
        """)

    def link_on_click(self, callback):
        self.onClick = callback

    def selected(self, number):
        print(number)
        self.number = number
        self.text = f"{number}"
        self.setText(f"{number}")

    def _on_clicked(self):
        """Wrapper that passes the button object (self) to the onClick callback"""
        if self.onClick:
            self.onClick(self)

    def has_been_extracted(self):
        """Mark button as extracted using custom property"""
        self.setProperty("extracted", True)
        self.style().unpolish(self)  # Reapply stylesheet
        self.style().polish(self)
    
    def reset_extraction_state(self):
        """Reset button to non-extracted state"""
        self.setProperty("extracted", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_focus(self, focused):
        """Set focus state using custom property"""
        self.setProperty("focus", focused)
        self.style().unpolish(self)
        self.style().polish(self)

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

    
