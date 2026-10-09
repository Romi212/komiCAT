# ui/theme.py
from dataclasses import dataclass, field, replace
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QObject, pyqtSignal, QSettings

@dataclass(frozen=True)
class Theme:
    name: str
    # neutrals
    window: str
    surface: str
    text: str
    border: str
    button_bg: str
    button_bg_hover: str
    popup_bg: str
    popup_text: str
    # accent family
    accent: str
    accent_hover: str
    accent_dim: str
    # highlights
    term_highlight: str
    term_highlight_alpha: int
    input_bg: str
    scroll_handle: str
    scroll_handle_hover: str
    dict_word: str
    # segment types: role -> (bg hex, bg alpha, border hex)
    segment_colors: dict = field(default_factory=dict)
    

    def qcolor(self, hex_str, alpha=255):
        c = QColor(hex_str)
        c.setAlpha(alpha)
        return c

DARK = Theme(
    name="Dark",
    window="#1f1f1f",          # dark gray instead of #121212
    surface="#262626",         # segment boxes, panels
    input_bg="#2d2d2d",        # text areas: slightly lighter than the window
    text="#eeeeee",
    border="#3c3c3c",
    button_bg="#2b2b2b", button_bg_hover="#373737",
    popup_bg="#2b2b2b", popup_text="#f0f0f0",
    scroll_handle="#555555", scroll_handle_hover="#777777",
    accent="#6e2130", accent_hover="#8a2e40", accent_dim="#4a1620",
    term_highlight="#ffeb3b", term_highlight_alpha=140,
    dict_word= "#4791ca",
    segment_colors={
        "text_bubble": ("#c80000", 50, "#ff0000"),
        "text_free":   ("#0000c8", 50, "#0000ff"),
        "sfx":         ("#00c800", 50, "#00ff00"),
    },
)
LIGHT = replace(DARK, name="Light",
    window="#f5f5f5", surface="#f9f9f9", input_bg="#ffffff", text="#222222",
    border="#cccccc", button_bg="#e2e2e2", button_bg_hover="#cccccc",
    popup_bg="#ffffff", popup_text="#222222",
    scroll_handle="#b5b5b5", scroll_handle_hover="#8f8f8f")
# add more: replace(DARK, name="Ocean", accent="#1f5f8b", ...)  (dataclasses.replace)

THEMES = {t.name: t for t in (DARK, LIGHT)}

class ThemeManager(QObject):
    theme_changed = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        saved = QSettings("Romi", "MangaCAT").value("theme", "Dark")
        self._theme = THEMES.get(saved, DARK)

    @property
    def theme(self):
        return self._theme

    def set_theme(self, name):
        self._theme = THEMES[name]
        QSettings("Romi", "MangaCAT").setValue("theme", name)
        self.theme_changed.emit(self._theme)

theme_manager = ThemeManager()   # module-level singleton
def current(): return theme_manager.theme

def build_qss(t):
    return f"""
    QMainWindow, QDialog {{ background-color: {t.window}; }}
    QWidget {{ color: {t.text}; }}

    QScrollArea {{ background-color: {t.window}; border: none; }}
    QScrollArea > QWidget > QWidget {{ background-color: {t.window}; }}

    QTextEdit, QPlainTextEdit, QLineEdit {{
        background-color: {t.input_bg};
        border: 1px solid {t.border};
        border-radius: 3px;
    }}

    QPushButton {{
        background-color: {t.button_bg};
        border: 1px solid {t.border};
        border-radius: 3px;
        padding: 4px 8px;
    }}
    QPushButton:hover {{ background-color: {t.button_bg_hover}; }}

    #combinedSegmentContainer {{ border: 2px solid {t.accent}; border-radius: 5px; }}

    /* rounded scrollbars */
    QScrollBar:vertical {{ background: transparent; width: 12px; margin: 2px; }}
    QScrollBar:horizontal {{ background: transparent; height: 12px; margin: 2px; }}
    QScrollBar::handle:vertical {{
        background: {t.scroll_handle}; border-radius: 4px; min-height: 30px;
    }}
    QScrollBar::handle:horizontal {{
        background: {t.scroll_handle}; border-radius: 4px; min-width: 30px;
    }}
    QScrollBar::handle:vertical:hover,
    QScrollBar::handle:horizontal:hover {{ background: {t.scroll_handle_hover}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
    QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}
    SegmentBox {{
                    border: 1px solid {t.border};
                    border-radius: 4px;
                    background-color:{t.surface};
                    
                              
    }}
    #combinedSegmentContainer {{ border: 2px solid {t.accent}; border-radius: 5px; }}
    #PageDivisionLabel {{font-weight: bold; border: none;}}
    #combineHighlight {{
        background-color: {t.accent_hover};
        border-radius: 3px;
    }}
    QLabel#DragHandle {{
        color:{t.text} ;
        font-size: 16px;
        font-weight: bold;
        background-color: {t.scroll_handle};
        border-radius: 3px;
    }}
    QLabel#DragHandle:hover {{
        background-color: {t.scroll_handle_hover};
        color: {t.text};
    }}
    QWidget#dictPopup {{  background-color: {t.popup_bg};
                        color: {t.popup_bg};
                        border: 1px solid #444;
                        border-radius: 6px; }}

    QTextBrowser#dictPopup {{ border: none;
                        background: transparent;
                        }}
    #termPopup {{
                    background-color: {t.button_bg};
                    color: {t.popup_text};
                    border: 1px solid #444;
                    border-radius: 4px;
                    padding: 4px 8px;
                }}
    QWidget#editMenu {{
                    background-color: {t.input_bg};
                    border: 1px solid {t.border};
                    border-radius: 8px;
                }}
    QWidget#editMenu QPushButton {{
                    min-width: 110px;
                    padding: 8px 10px;
                    border-radius: 6px;
                }}
                
           
    """

def apply(app):
    app.setStyleSheet(build_qss(current()))
    theme_manager.theme_changed.connect(lambda t: app.setStyleSheet(build_qss(t)))