# ui/theme.py
from dataclasses import dataclass, field, replace
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QObject, pyqtSignal, QSettings

from storage.resources import APP_FONT
APP_FONT_CSS = f' "Yu Gothic UI", "Meiryo UI", "Segoe UI", sans-serif'


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
    surface_confirmed: str 
    confirmed_badge: str
    # segment types: role -> (bg hex, bg alpha, border hex)
    segment_colors: dict = field(default_factory=dict)
    badge_text: str = "#ffffff"
    focus_border: str = "#ffffff"
    arrow: str = "#b5223f"
    arrow_hover: str = "#d03a58"
    panel_border: str = "#9c3a52"
    panel_label_bg: str = "#9c3a52"
    panel_label_bg: str = "#9c3a52"   # light rose pill
    page_label_text: str = "#e8b4be"   # dark burgundy, readable on the pill
    def segment_style(self, seg_type):
        bg_hex, alpha, border_hex, badge_hex = self.segment_colors[seg_type.key]
        return {
            "bg": self.qcolor(bg_hex, alpha),
            "border": QColor(border_hex),
            "badge": QColor(badge_hex),
            "badge_text": QColor(self.badge_text),
        }

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
    surface_confirmed = "#262626",     # lighter, slightly greenish
    confirmed_badge = "#3e7d4a",
    
        segment_colors={
        #               bg        alpha  border     badge
        "text_bubble": ("#e0566e", 85,  "#b5223f", "#b5223f"),
        "text_free":   ("#e0566e", 85,  "#9c3a52", "#9c3a52"),
        "sfx":         ("#f2a58b", 110, "#e8896e", "#e8896e"),
    },
    
)
LIGHT = replace(DARK, name="Light",
    window="#f5f5f5", surface="#f9f9f9", input_bg="#ffffff", text="#222222",
    border="#cccccc", button_bg="#e2e2e2", button_bg_hover="#cccccc",
    popup_bg="#ffffff", popup_text="#222222",
    scroll_handle="#b5b5b5", scroll_handle_hover="#8f8f8f",surface_confirmed="#e3efe3", confirmed_badge="#5aa469")
# add more: replace(DARK, name="Ocean", accent="#1f5f8b", ...)  (dataclasses.replace)

SAKURA = replace(DARK, name="Sakura",
    # window = lightest pink, used ONLY for the page background
    window="#ffd9d9",
    # segments, panels, buttons, inputs all share the slightly darker pink
    surface="#f9c3c3",
    input_bg="#f9c3c3",
    button_bg="#f9c3c3", button_bg_hover="#f0abb0",
    text="#4a1620",
    border="#c9626f",
    popup_bg="#f9c3c3", popup_text="#4a1620",
    scroll_handle="#d98c97", scroll_handle_hover="#c4697a",
    accent="#6e2430", accent_hover="#8f3040", accent_dim="#5a1e24",
    term_highlight="#ffb3a0", term_highlight_alpha=150,
    dict_word="#a62a45",
    surface_confirmed="#f9c3c3", confirmed_badge="#b5384a",
    arrow="#b5223f", arrow_hover="#d03a58",
    panel_border="#9c3a52", panel_label_bg="#6e2430",
   page_label_text="#ffffff",
)

THEMES = {t.name: t for t in (DARK, LIGHT, SAKURA)}

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
    QWidget {{ color: {t.text}; font-family: {APP_FONT_CSS}; }}
    QPushButton#coverButton {{
        border: 1px solid {t.border};
        border-radius: 4px;
        background-color: {t.input_bg};
        padding: 0;
        }}
    QWidget#loadingOverlay {{ background-color: rgba(0, 0, 0, 120); }}
    QPushButton#coverButton:hover {{ border: 2px solid {t.accent}; }}
    QFrame#recentPanel {{
        background-color: {t.surface};
        border: 2px solid {t.border};
        border-radius: 10px;
    }}
    QLabel#launcherTitle {{
        color: {t.text};
        font-family: "Rampart One", {APP_FONT_CSS};
        font-size: 30pt;
        font-weight: bold;
        letter-spacing: 2px;
    }}
    QLabel#recentTitle {{
        font-size: 10pt;
        font-weight: bold;
        color: {t.text};
        background: transparent;
        border: none;
    }}
    QLabel#errorBubbleText {{
        color: {t.text};
        font-family: "Rampart One", {APP_FONT_CSS};
        font-size: 20pt;
        font-weight: bold;
        background: transparent;
        border: none;
    }}
    QFrame#errorPanel {{
        background-color: {t.surface};
        border: 2px solid {t.border};
        border-radius: 10px;
    }}
    QLabel#errorMessage {{
        color: #e5534b;
        font-weight: bold;
        background: transparent;
        border: none;
    }}
    QLabel#errorSolution {{
        color: {t.text};
        background: transparent;
        border: none;
    }}
    QPushButton#errorOkButton {{
        padding: 6px 24px;
    }}
    QPushButton#prefsButton {{
        background-color: transparent;
        color: {t.text};
        border: 1px solid transparent;
        border-radius: 18px;
        font-size: 14pt;
    }}
    QPushButton#prefsButton:hover {{
        background-color: {t.button_bg_hover};
        border-color: {t.border};
    }}
    QLabel#launcherTitle {{
        color: {t.text};
        font-size: 30pt;
        font-weight: bold;
        letter-spacing: 2px;
    }}
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
    QFrame#segmentDivider {{ background-color: {t.border}; border: none; }}

    QLabel#numberBadge {{
        background-color: {t.scroll_handle};
        border-radius: 3px;
        font-size: 10px;
    }}

    SegmentBox QTextEdit {{ background: transparent; border: none; }}
    #combinedSegmentContainer {{ border: 2px solid {t.accent}; border-radius: 5px; }}
    QLabel#PageDivisionLabel {{
        background-color: {t.accent};
        color: {t.page_label_text};
        border: none;
        border-radius: 8px;
        padding: 2px 12px;
        font-weight: bold;
    }}
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
    SegmentBox[confirmed="true"] {{
        background-color: {t.surface_confirmed};
        border: 1px solid {t.confirmed_badge};
    }}
    QLabel#confirmedBadge {{
        background-color: {t.confirmed_badge};
        color: #ffffff;
        border-radius: 3px;
        font-size: 11px;
        font-weight: bold;
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
    QPushButton#acceptSuggestion {{
        background-color: {t.accent};
        color: #ffffff;
        border: none;
        border-radius: 3px;
        padding: 1px 8px;
        font-size: 10px;
    }}
    QPushButton#acceptSuggestion:hover {{ background-color: {t.accent_hover}; }}
        QWidget {{ background-color: {t.window}; color: {t.text}; }}
    QMainWindow, QDialog, QMessageBox {{ background-color: {t.window}; }}

    QLabel, QCheckBox, QRadioButton, QGroupBox {{ background: transparent; }}

    QComboBox, QSpinBox, QDoubleSpinBox {{
        background-color: {t.input_bg};
        color: {t.text};
        border: 1px solid {t.border};
        border-radius: 3px;
        padding: 3px 6px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {t.input_bg};
        color: {t.text};
        border: 1px solid {t.border};
        selection-background-color: {t.accent};
        selection-color: #ffffff;
    }}

    QMenuBar {{ background-color: {t.window}; color: {t.text}; }}
    QMenuBar::item:selected {{ background-color: {t.button_bg_hover}; }}
    QMenu {{
        background-color: {t.popup_bg};
        color: {t.popup_text};
        border: 1px solid {t.border};
    }}
    QMenu::item {{ padding: 5px 24px; }}
    QMenu::item:selected {{ background-color: {t.accent}; color: #ffffff; }}
    QMenu::separator {{ height: 1px; background: {t.border}; margin: 4px 8px; }}

    QToolTip {{
        background-color: {t.popup_bg};
        color: {t.popup_text};
        border: 1px solid {t.border};
    }}          
           
    """

def apply(app):
    font = app.font()
    font.setPointSize(11)          # or font.setPixelSize(16)
    app.setFont(font)
    app.setStyleSheet(build_qss(current()))
    theme_manager.theme_changed.connect(lambda t: app.setStyleSheet(build_qss(t)))