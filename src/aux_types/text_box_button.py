
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt


class TextBoxButton(QPushButton):
    def __init__(self, text_box, width=80, height=30, alpha=0.6):
        super().__init__()
        self.text_box = text_box
        self.text = ""
        self.number = 0
        self.onClick = None
        self.has_been_extracted_flag = False
        
        # Make button checkable to maintain pressed state
        self.setCheckable(True)
        
        # Connect to a wrapper that passes the button object instead of the boolean signal
        self.clicked.connect(self._on_clicked)
        
        # Set custom properties for state management
        self.setProperty("state", "not_extracted")
        
        
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
                font-size: 52px;
                padding: 2px 0px 0px 2px;
                
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
            QPushButton[state="extracted"] {{
                background-color: rgba(0, 0, 0, 0);
                border: 1px solid gray;
                color: transparent;
            }}
            QPushButton[state="extracted"]:hover {{
                background-color: rgba(0, 0, 0, 0);
            }}
            QPushButton[state="extracted"]:checked {{
                background-color: rgba(0, 0, 0, 0);
                border: 1px solid gray;
            }}
            QPushButton[state="focused"] {{
                background-color: rgba(0, 0, 0, 0);
                border: 4px solid blue;
                color: transparent;
            }}
            QPushButton[state="focused"]:hover {{
                background-color: rgba(0, 0, 0, 0);
            }}
            QPushButton[state="focused"]:checked {{
                background-color: rgba(0, 0, 0, 0);
                border: 4px solid blue;
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
        self.has_been_extracted_flag = True
        self.setProperty("state", "extracted")
        self.style().unpolish(self)  # Reapply stylesheet
        self.style().polish(self)
    
    def reset_extraction_state(self):
        """Reset button to non-extracted state"""
        self.setProperty("state", "not_extracted")
        self.style().unpolish(self)
        self.style().polish(self)

    def set_focus(self, focused):
        """Set focus state using custom property"""
        print(f"Setting focus to {focused} for button with text '{self.text}'")
        self.setProperty("state", "focused" if focused else "extracted")
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

    def uncheck(self):
        """Uncheck the button and reset state"""
        self.setChecked(False)
        self.setText("")
        self.setProperty("state", "not_extracted")
        self.style().unpolish(self)
        self.style().polish(self)
