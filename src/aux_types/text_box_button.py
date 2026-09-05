
from PyQt6.QtWidgets import QPushButton, QGraphicsItem
from PyQt6.QtCore import Qt, QRectF


class TextBoxButton(QPushButton):
    
    def __init__(self, text_box, width=80, height=30, alpha=0.6):
        super().__init__()
        self.segment = None
        #Es necesario guardar el text box para extraer el texto
        self.text_box = text_box
        self.text = ""
        self.number = 0
        self.onClick = None
        self.has_been_extracted_flag = False

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Make button checkable to maintain pressed state
        self.setCheckable(True)
        
        # Connect to a wrapper that passes the button object instead of the boolean signal
        self.clicked.connect(self._on_clicked)
        
        # Set custom properties for state management
        self.setProperty("state", "not_extracted")
        
        
        # Set fixed size
        self.setFixedSize(width, height)
        self.setMouseTracking(True)

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

    def _get_hit_zone(self, pos):
        """Determine if mouse is near an edge/corner or in the center."""
        margin = 8  # Edge detection margin in pixels
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()

        left = x < margin
        right = x > w - margin
        top = y < margin
        bottom = y > h - margin

        if top and left: return "TL"
        if top and right: return "TR"
        if bottom and left: return "BL"
        if bottom and right: return "BR"
        if left: return "L"
        if right: return "R"
        if top: return "T"
        if bottom: return "B"
        return "MOVE"

    def _update_cursor(self, zone):
        """Set appropriate resize cursor based on hover zone."""
        cursors = {
            "TL": Qt.CursorShape.SizeFDiagCursor,
            "BR": Qt.CursorShape.SizeFDiagCursor,
            "TR": Qt.CursorShape.SizeBDiagCursor,
            "BL": Qt.CursorShape.SizeBDiagCursor,
            "L": Qt.CursorShape.SizeHorCursor,
            "R": Qt.CursorShape.SizeHorCursor,
            "T": Qt.CursorShape.SizeVerCursor,
            "B": Qt.CursorShape.SizeVerCursor,
            "MOVE": Qt.CursorShape.ArrowCursor
        }
        self.setCursor(cursors.get(zone, Qt.CursorShape.ArrowCursor))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.has_been_extracted_flag:
            self._global_drag_start = event.globalPosition()
            self._has_moved = False
            self._hit_zone = self._get_hit_zone(event.position())

            proxy = self.graphicsProxyWidget()
            if proxy and proxy.scene():
                self._start_proxy_pos = proxy.pos()
                self._start_scene_mouse_pos = proxy.mapToScene(event.position())
                self._start_size = (self.width(), self.height())

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not event.buttons():
            zone = self._get_hit_zone(event.position())
            self._update_cursor(zone)
            super().mouseMoveEvent(event)
            return
        
        if (event.buttons() & Qt.MouseButton.LeftButton) and hasattr(self, '_start_scene_mouse_pos') and not self.has_been_extracted_flag:
            # Check drag threshold (3 pixels)
            global_delta = event.globalPosition() - self._global_drag_start
            if abs(global_delta.x()) + abs(global_delta.y()) > 3:
                self._has_moved = True

            proxy = self.graphicsProxyWidget()
            if proxy and proxy.scene():
                # Calculate current mouse position in scene coordinates
                current_scene_mouse_pos = proxy.mapToScene(event.position())
                
                # Calculate exact displacement delta
                delta = current_scene_mouse_pos - self._start_scene_mouse_pos

#resize part
                start_w, start_h = self._start_size
                start_x, start_y = self._start_proxy_pos.x(), self._start_proxy_pos.y()
                min_size = 20  # Prevent shrinking box to 0

                zone = getattr(self, '_hit_zone', 'MOVE')

                if zone == "MOVE":
                    # Standard drag move
                    proxy.setPos(self._start_proxy_pos + delta)
                else:
                    # Handle Resizing
                    new_w, new_h = start_w, start_h
                    new_x, new_y = start_x, start_y

                    # Horizontal resizing
                    if "R" in zone:
                        new_w = max(min_size, start_w + delta.x())
                    elif "L" in zone:
                        possible_w = start_w - delta.x()
                        if possible_w >= min_size:
                            new_w = possible_w
                            new_x = start_x + delta.x()
                        else:
                            new_w = min_size
                            new_x = start_x + (start_w - min_size)

                    # Vertical resizing
                    if "B" in zone:
                        new_h = max(min_size, start_h + delta.y())
                    elif "T" in zone:
                        possible_h = start_h - delta.y()
                        if possible_h >= min_size:
                            new_h = possible_h
                            new_y = start_y + delta.y()
                        else:
                            new_h = min_size
                            new_y = start_y + (start_h - min_size)

                    int_w, int_h = int(new_w), int(new_h)
                    proxy.setCacheMode(QGraphicsItem.CacheMode.NoCache)
                    proxy.prepareGeometryChange()
                    self.setFixedSize(int_w, int_h)
                    proxy.setGeometry(QRectF(float(new_x), float(new_y), float(int_w), float(int_h)))

                    self.style().unpolish(self)
                    self.style().polish(self)
                    # Invalidate style cache and force repaint
                    
                    self.update()
                    proxy.scene().update(proxy.sceneBoundingRect())
              
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if hasattr(self, '_has_moved') and self._has_moved:
            # If we dragged the button, intercept the release event and DO NOT call super().
            # This prevents the button from triggering a "click" and selecting the bubble.
            self._has_moved = False
            self.setDown(False) # Visually un-press the button
            return
            
        # If it was just a normal click without dragging, let it trigger the selection
        super().mouseReleaseEvent(event)

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

    def set_segment(self, segment):
        self.segment = segment
